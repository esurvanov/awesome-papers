"""Сборка ролика с озвучкой: текст диктора → речь → сцены в темпе речи → один mp4.

Запуск (из корня репозитория), аргумент — папка статьи с passport.py, narration.py, scenes.py:
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap                    # локальный голос Silero xenia (по умолчанию)
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap --clean 2          # сильнее чистка от «песка» (0…3)
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap --engine realtime  # живая модель OpenAI, голос cedar
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap --only A05 F09     # пересобрать только эти сцены
Ключ OpenAI — OPENAI_API_KEY в .env.local в корне репозитория (в git не попадает).

Что делает для каждой сцены из ORDER (narration.py статьи):
  1. озвучивает TEXT[сцена] (кэш в videos/<папка>/audio/, пересчитывается при смене текста или настроек голоса);
     голос OpenAI проверяется обратным распознаванием: если фраза оборвана или прочитана не дословно, озвучка повторяется;
  2. рендерит сцену черновиком при SLOW=1 и меряет длину анимации (запоминается, пока не изменится код сцен);
  3. подбирает SLOW так, чтобы анимация шла столько же, сколько речь, и рендерит начисто;
  4. накладывает речь; если речь всё же длиннее, держит последний кадр.
Темп речи закреплён числом (--wpm): медленную запись ускоряем без изменения высоты голоса.
Уже собранные сцены (та же запись, тот же код сцен) при перезапуске пропускаются.
Сцены должны читать темп из переменной окружения SLOW (manimkit.story_base или своя Base).
Результат — videos/<папка>/<папка>_<движок>.mp4 (videos/ в git не попадает).
"""
import argparse
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402  голоса OpenAI, ударения, инструкция голосу

ROOT = Path(__file__).resolve().parents[2]  # корень репозитория
VIDEOS = ROOT / "videos"
LEAD, TAIL = 0.4, 0.8  # тишина до речи и после неё, секунды


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout
    return float(out.strip())


def _words(s):
    return re.sub(r"[^а-яa-z0-9 ]", "", s.lower().replace("ё", "е")).split()


def transcribe(wav):
    import uuid
    boundary = uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\ngpt-4o-mini-transcribe\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nru\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode()
        + wav.read_bytes() + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    req = urllib.request.Request("https://api.openai.com/v1/audio/transcriptions", data=b"".join(parts), headers={
        "Authorization": f"Bearer {voice.openai_key()}", "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["text"]


def heard_ok(wav, text):
    """Голос OpenAI иногда обрывает последнюю фразу, а разговорная модель может что-то пересказать своими словами:
    распознаём запись обратно и сверяем окончание и текст целиком (по словам, с допуском на ошибки распознавания)."""
    import difflib
    got = transcribe(wav)
    w, g = _words(text), _words(got)
    ratio = difflib.SequenceMatcher(None, w, g).ratio()
    return w[-2:] == g[-2:] and ratio >= 0.8, got, ratio


def fix_tempo(wav, text, wpm):
    """Темп закреплён числом: если голос медленнее wpm слов в минуту — ускорить запись без изменения высоты голоса."""
    words = len(_words(text))
    now = words / (duration(wav) / 60)
    if now < wpm * 0.97:
        k = min(1.3, wpm / now)  # больше ×1.3 не ускоряем: ×1.4 на слух уже «очень быстро»
        tmp = wav.with_suffix(".tempo.wav")
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", f"atempo={k:.3f}", str(tmp)])
        tmp.replace(wav)
        print(f"  темп {now:.0f} → {now * k:.0f} слов/мин", flush=True)


def shift_pitch(wav, semitones):
    """Сдвинуть высоту голоса на semitones полутонов, сохранив длительность."""
    if not semitones:
        return
    k = 2 ** (semitones / 12)
    rate = int(sh(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=sample_rate", "-of", "csv=p=0", str(wav)]).stdout)
    tmp = wav.with_suffix(".pitch.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", f"asetrate={rate}*{k:.5f},aresample={rate},atempo={1 / k:.5f}", str(tmp)])
    tmp.replace(wav)


def tts(text, out_wav, a):
    """Озвучить фразу; для голосов OpenAI — проверить обратным распознаванием и при расхождении повторить."""
    if a.engine == "say":
        aiff = out_wav.with_suffix(".aiff")
        sh(["say", "-v", a.voice, "-r", "170", "-o", str(aiff), text])
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "1", str(out_wav)])
        aiff.unlink()
        return
    spoken = voice.stress(text) if a.stress else text
    for attempt in range(1, 4):
        raw = out_wav.with_suffix(".raw.wav")
        raw.write_bytes(voice.ENGINES[a.engine](spoken, a.model, a.voice))
        # чистка (для Silero) и одинаковое выравнивание громкости для всех фраз
        chain = ",".join(x for x in (voice.CLEAN.get(a.clean, "") if a.engine == "silero" else "", "loudnorm=I=-16:TP=-1.5:LRA=11") if x)
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", chain, "-ar", "48000", "-ac", "1", str(out_wav)])
        raw.unlink()
        if a.engine == "silero":  # локальный голос читает ровно данный текст — сверка через OpenAI не нужна
            fix_tempo(out_wav, text, a.wpm)
            return
        ok, got, ratio = heard_ok(out_wav, text)
        if ok:
            fix_tempo(out_wav, text, a.wpm)
            shift_pitch(out_wav, a.pitch)
            return
        print(f"  озвучка не совпала с текстом (сходство {ratio:.2f}, конец: …{' '.join(_words(got)[-4:])}), попытка {attempt}", flush=True)
    raise SystemExit("Голос трижды прочитал фразу не так — сократите или перефразируйте её")


def render(scene_file, scene, slow, hd, out_dir):
    env = dict(os.environ, SLOW=f"{slow:.4f}")
    sh(["manimgl", str(scene_file), scene, "-w", "--hd" if hd else "-l", "--video_dir", str(out_dir)], cwd=ROOT, env=env)
    return out_dir / f"{scene}.mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper", help="папка статьи, например papers/2610.23637-relation-gap")
    ap.add_argument("--engine", choices=["silero", "say", "speech", "chat", "realtime"], default="silero",
                    help="silero — локальный русский голос (по умолчанию, xenia); say — Милена (macOS); speech, chat, realtime — голоса OpenAI")
    ap.add_argument("--clean", type=int, default=1, choices=[0, 1, 2, 3], help="чистка голоса Silero от «песка»: 0 — нет … 3 — сильная")
    ap.add_argument("--model", default=None, help="по умолчанию: speech — gpt-4o-mini-tts-2025-03-20, chat — gpt-audio-1.5, realtime — gpt-realtime-2.1")
    ap.add_argument("--voice", default=None, help="say: Milena; OpenAI: cedar, marin, …")
    ap.add_argument("--stress", dest="stress", action="store_true", default=None, help="расставлять ударения программой RUAccent")
    ap.add_argument("--no-stress", dest="stress", action="store_false", help="не расставлять ударения")
    ap.add_argument("--wpm", type=float, default=115, help="целевой темп речи, слов в минуту (медленнее — ускоряем запись); 115 выбрано на слух 20.10.2026")
    ap.add_argument("--pitch", type=float, default=0, help="сдвиг высоты голоса в полутонах (−2 — ниже); темп при этом сохраняется")
    ap.add_argument("--only", nargs="*", help="пересобрать только эти сцены (остальные берутся готовыми)")
    a = ap.parse_args()
    a.voice = a.voice or {"say": "Milena", "silero": "xenia"}.get(a.engine, "cedar")
    if a.stress is None:  # Silero с разметкой RUAccent звучит роботизированнее (на слух 21.10.2026) — ставит ударения сам
        a.stress = a.engine != "silero"
    a.model = a.model or {"say": "", "silero": "v4_ru", "speech": "gpt-4o-mini-tts-2025-03-20", "chat": "gpt-audio-1.5", "realtime": "gpt-realtime-2.1"}[a.engine]

    paper = (ROOT / a.paper).resolve()
    slug = paper.name
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    scene_file = paper / getattr(nar, "SCENE_FILE", "scenes.py")
    adir, vdir, rdir = VIDEOS / slug / "audio", VIDEOS / slug / "voiced", VIDEOS / slug / "render"
    for d in (adir, vdir, rdir):
        d.mkdir(parents=True, exist_ok=True)

    bfile = vdir / "base_durations.json"
    bcache = json.loads(bfile.read_text()) if bfile.exists() else {}
    kit = ROOT / "core" / "manimkit"
    code = hashlib.sha1(scene_file.read_bytes() + (kit / "style.py").read_bytes() + (kit / "story.py").read_bytes()).hexdigest()[:12]

    parts = []
    for scene in nar.ORDER:
        bkey = f"{scene}:{code}"
        out = vdir / f"{scene}.mp4"
        parts.append(out)
        if a.only and scene not in a.only and out.exists():
            continue
        text = nar.TEXT[scene]
        wav = adir / f"{scene}.{a.engine}.wav"
        tag = adir / f"{scene}.{a.engine}.hash"
        h = hashlib.sha1(f"{a.model}|{a.voice}|{a.stress}|{a.wpm}|{a.pitch}|{a.clean}|{voice.VOICE_STYLE}|{voice.SAY_LATIN}|{text}".encode()).hexdigest()
        if not wav.exists() or not tag.exists() or tag.read_text() != h:
            tts(text, wav, a)
            tag.write_text(h)
        speech = duration(wav)
        # сцена уже собрана с этой же речью и этим же кодом — не пересобираем
        key = vdir / f"{scene}.key"
        done = f"{a.engine}:{hashlib.sha1(wav.read_bytes()).hexdigest()[:12]}:{code}"  # по самой записи: новая запись — новая сборка
        if out.exists() and key.exists() and key.read_text() == done:
            print(f"{scene}: готова, пропуск", flush=True)
            continue

        # длина анимации при SLOW=1 зависит только от кода сцен — запоминаем, чтобы не рендерить черновик повторно
        if bkey not in bcache:
            bcache[bkey] = duration(render(scene_file, scene, 1.0, False, rdir))
            bfile.write_text(json.dumps(bcache, indent=1))
        base = bcache[bkey]
        slow = max(1.0, (LEAD + speech + TAIL) / base)
        vid = render(scene_file, scene, slow, True, rdir)
        vlen = duration(vid)
        total = max(vlen, LEAD + speech + TAIL)
        delay = int(LEAD * 1000)
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-filter_complex",
            f"[0:v]tpad=stop_mode=clone:stop_duration={total - vlen + 0.05:.3f}[v];"
            f"[1:a]adelay={delay}|{delay},apad[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", str(out)])
        key.write_text(done)
        print(f"{scene}: речь {speech:5.1f} с, анимация {base:5.1f} → {vlen:5.1f} с (темп ×{slow:.2f}), итог {total:5.1f} с", flush=True)

    lst = vdir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = VIDEOS / slug / f"{slug}_{a.engine}.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)])
    print(f"Готово: {final} ({duration(final):.0f} с)")


if __name__ == "__main__":
    main()
