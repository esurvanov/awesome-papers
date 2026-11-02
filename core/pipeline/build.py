"""Сборка ролика с озвучкой: текст диктора → речь → сцены в темпе речи → один mp4.

Запуск (из корня репозитория), аргумент — папка статьи с passport.py, narration.py, scenes.py:
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap                    # голос по умолчанию: OpenAI gpt-realtime-2.1, verse
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap --engine silero    # запасной локальный голос Silero xenia
    uv run python core/pipeline/build.py papers/2610.23637-relation-gap --clean 2          # для Silero: сильнее чистка от «песка» (0…3)
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
import board  # noqa: E402  рисунок «от руки» поверх сцены (narration.BOARD)

ROOT = Path(__file__).resolve().parents[2]  # корень репозитория
VIDEOS = ROOT / "videos"
LEAD, TAIL = 0.4, 0.8  # тишина до речи и после неё, секунды


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path):
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout
    return float(out.strip())


NUMERAL = re.compile(r"^(?:ноль|нул|один|одн|два|две|двух|двум|тр[её]х|три|четыр|пят|шест|сем|восем|восьм|девят|десят|"
                     r"одиннадцат|двенадцат|сорок|девяност|сто(?![а-яё])|ста(?![а-яё])|двест|трист|сот|тысяч|миллион|миллиард|половин|полтор)")


def _words(s):
    return re.sub(r"[^а-яa-z0-9 ]", "", s.lower().replace("ё", "е")).split()


def transcribe(wav, hint=""):
    """Распознавание для сверки; hint — подсказка по написанию (числа словами, имена как в тексте), не сам текст:
    подсказка текстом целиком подтягивала бы распознавание к ожидаемому и прятала бы ошибки голоса."""
    import uuid
    boundary = uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"prompt\"\r\n\r\n{hint}\r\n".encode(),
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
    names = sorted({m for m in re.findall(r"[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*", text.replace("\u0301", "")) if " " in m or len(m) > 3})
    got = transcribe(wav, "Числа записывай словами, как произнесены. Имена и названия: " + ", ".join(names) + ".")
    # числа распознавание пишет цифрами («19»), а в тексте они словами («девятнадцати») — сверяем без чисел с обеих сторон
    w = [x for x in _words(text) if not NUMERAL.match(x)]
    g = [x for x in _words(got) if not re.search(r"\d", x) and not NUMERAL.match(x)]
    ratio = difflib.SequenceMatcher(None, w, g).ratio()
    # числа — отдельно: их выкинули из сравнения текста, и «шестьдесят» звучало как «сетидисят» незамеченным.
    # Каждое число текста должно найтись в распознанном (по началу слова); если распознавание дало цифры — их не сверить
    nums = [x for x in _words(text) if NUMERAL.match(x)]
    heard = _words(got)
    digits = any(re.search(r"\d", x) for x in heard)
    missing = [x for x in nums if not any(h[:4] == x[:4] for h in heard)]
    if missing and not digits:
        print(f"  числа не распознаны: {', '.join(missing)}", flush=True)
        return False, got, ratio
    if missing and digits:
        print(f"  ⚠ числа записаны цифрами — проверить на слух: {', '.join(missing)}", flush=True)
    return w[-2:] == g[-2:] and ratio >= 0.8, got, ratio


def fix_tempo(wav, text, wpm):
    """Темп закреплён числом: если голос медленнее wpm слов в минуту — ускорить запись без изменения высоты голоса."""
    if not wpm:
        return
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


def tts(text, out_wav, a, vtext=None):
    """Озвучить фразу; для голосов OpenAI — проверить обратным распознаванием и при расхождении повторить.
    vtext — текст для голоса (фонетическая запись трудных мест); сверка распознанного идёт с экранным text."""
    if a.engine == "say":
        aiff = out_wav.with_suffix(".aiff")
        sh(["say", "-v", a.voice, "-r", "170", "-o", str(aiff), text])
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "1", str(out_wav)])
        aiff.unlink()
        return
    vtext = vtext or text
    spoken = voice.stress(vtext) if a.stress and "\u0301" not in vtext else vtext  # ударения, расставленные в тексте вручную, главнее RUAccent
    for attempt in range(1, 4):
        raw = out_wav.with_suffix(".raw.wav")
        raw.write_bytes(voice.ENGINES[a.engine](spoken, a.model, a.voice, style=a.style))
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


def render(scene_file, scene, slow, hd, out_dir, engine="realtime", sync_abs=False):
    env = dict(os.environ, SLOW=f"{slow:.4f}", VOICE_ENGINE=engine)  # сцена ждёт начала фраз по этой озвучке (story.beat)
    if sync_abs:
        env["SYNC"] = "abs"
    sh(["manimgl", str(scene_file), scene, "-w", "--hd" if hd else "-l", "--video_dir", str(out_dir)], cwd=ROOT, env=env)
    return out_dir / f"{scene}.mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper", help="папка статьи, например papers/2610.23637-relation-gap")
    ap.add_argument("--engine", choices=["silero", "say", "speech", "chat", "realtime"], default=voice.DEFAULT["engine"],
                    help="realtime — живая модель OpenAI (по умолчанию, verse); silero — локальный русский голос (xenia); say — Милена; speech, chat — OpenAI")
    ap.add_argument("--clean", type=int, default=1, choices=[0, 1, 2, 3], help="чистка голоса Silero от «песка»: 0 — нет … 3 — сильная")
    ap.add_argument("--model", default=None, help="по умолчанию: speech — gpt-4o-mini-tts-2025-03-20, chat — gpt-audio-1.5, realtime — gpt-realtime-2.1")
    ap.add_argument("--voice", default=None, help="say: Milena; silero: xenia; OpenAI: verse (по умолчанию), marin, cedar, …")
    ap.add_argument("--stress", dest="stress", action="store_true", default=None, help="расставлять ударения программой RUAccent")
    ap.add_argument("--no-stress", dest="stress", action="store_false", help="не расставлять ударения")
    ap.add_argument("--wpm", type=float, default=None,
                    help="целевой темп речи, слов в минуту (медленнее — ускоряем запись); 0 — не трогать. По умолчанию: голос по умолчанию — как есть, Silero — 115")
    ap.add_argument("--pitch", type=float, default=0, help="сдвиг высоты голоса в полутонах (−2 — ниже); темп при этом сохраняется")
    ap.add_argument("--only", nargs="*", help="пересобрать только эти сцены (остальные берутся готовыми)")
    ap.add_argument("--voice-only", action="store_true", help="только озвучка — для раскадровки (core/pipeline/animatic.py), без рендера сцен")
    a = ap.parse_args()
    a.voice = a.voice or {"say": "Milena", "silero": "xenia"}.get(a.engine, voice.DEFAULT["voice"])
    if a.wpm is None:  # 115 выбрано на слух 20.10.2026 для Silero и cedar; verse звучит хорошо в своём темпе
        a.wpm = voice.DEFAULT["wpm"] if (a.engine, a.voice) == (voice.DEFAULT["engine"], voice.DEFAULT["voice"]) else 115
    if a.stress is None:  # Silero с разметкой RUAccent звучит роботизированнее (на слух 21.10.2026) — ставит ударения сам
        a.stress = a.engine != "silero"
    a.model = a.model or {"say": "", "silero": "v4_ru", "speech": "gpt-4o-mini-tts-2025-03-20", "chat": "gpt-audio-1.5", "realtime": "gpt-realtime-2.1"}[a.engine]

    paper = (ROOT / a.paper).resolve()
    slug = paper.name
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    a.style = voice.voice_style(**getattr(nar, "VOICE_OVERRIDE", {}))  # блоки указания голосу; статья может заменить свои
    scene_file = paper / getattr(nar, "SCENE_FILE", "scenes.py")
    adir, vdir, rdir = VIDEOS / slug / "audio", VIDEOS / slug / "voiced", VIDEOS / slug / "render"
    for d in (adir, vdir, rdir):
        d.mkdir(parents=True, exist_ok=True)

    bfile = vdir / "base_durations.json"
    bcache = json.loads(bfile.read_text()) if bfile.exists() else {}
    kit = ROOT / "core" / "manimkit"
    code = hashlib.sha1(scene_file.read_bytes() + (kit / "style.py").read_bytes() + (kit / "story.py").read_bytes()
                        + (Path(__file__).parent / "board.py").read_bytes() + (Path(__file__).parent / "timing.py").read_bytes() + repr(getattr(nar, "BOARD", {})).encode()).hexdigest()[:12]

    # ворота 1 (закон 32–34): текст проверен — ударения по реестру, обыденная лексика, текст на слух; иначе озвучку не начинаем
    import text_check
    terr = text_check.check(paper)
    if terr:
        for e in terr[:40]:
            print("  ✗", e)
        raise SystemExit(f"Ворота текста: {len(terr)} нарушений — сначала исправить текст (core/pipeline/text_check.py)")

    parts = []
    for scene in nar.ORDER:
        bkey = f"{scene}:{code}"
        out = vdir / f"{scene}.mp4"
        parts.append(out)
        if a.only and scene not in a.only and out.exists():
            continue
        text = nar.TEXT[scene]
        vtext = voice.for_voice(text, getattr(nar, "SAY_AS", {}))  # текст для голоса: фонетическая запись трудных мест (закон 33)
        wav = adir / f"{scene}.{a.engine}.wav"
        tag = adir / f"{scene}.{a.engine}.hash"
        h = hashlib.sha1(f"{a.model}|{a.voice}|{a.stress}|{a.wpm}|{a.pitch}|{a.clean}|{a.style}|{voice.VERBATIM}|{voice.SAY_LATIN}|{vtext}".encode()).hexdigest()
        if not wav.exists() or not tag.exists() or tag.read_text() != h:
            tts(text, wav, a, vtext)
            tag.write_text(h)
        speech = duration(wav)
        if a.voice_only:
            print(f"{scene}: озвучка {speech:5.1f} с", flush=True)
            continue
        bkey = f"{scene}:{code}:{hashlib.sha1(wav.read_bytes()).hexdigest()[:12]}"  # длина анимации зависит и от записи: сцена ждёт её фраз
        # сцена уже собрана с этой же речью и этим же кодом — не пересобираем
        key = vdir / f"{scene}.key"
        done = f"{a.engine}:{hashlib.sha1(wav.read_bytes()).hexdigest()[:12]}:{code}"  # по самой записи: новая запись — новая сборка
        if out.exists() and key.exists() and key.read_text() == done:
            print(f"{scene}: готова, пропуск", flush=True)
            continue

        sync_abs = getattr(nar, "SYNC", None) == "abs"  # точный синхрон: сцена сама ждёт фраз по записи, темп не растягиваем (закон 30)
        # длина анимации при SLOW=1 зависит только от кода сцен — запоминаем, чтобы не рендерить черновик повторно
        if sync_abs:
            bcache[bkey] = bcache.get(bkey, 0.0)
        elif bkey not in bcache:
            bcache[bkey] = duration(render(scene_file, scene, 1.0, False, rdir, a.engine))
            bfile.write_text(json.dumps(bcache, indent=1))
        base = bcache[bkey]
        slow = 1.0 if sync_abs else max(1.0, (LEAD + speech + TAIL) / base)
        vid = render(scene_file, scene, slow, True, rdir, a.engine, sync_abs)
        if sync_abs:
            base = duration(vid)
        if scene in getattr(nar, "BOARD", {}):  # рука дорисовывает части поверх сцены под слова диктора
            layer, cues = nar.BOARD[scene]
            vid = board.hand_overlay(vid, scene_file, layer, cues, text, speech, LEAD, rdir / "hand")
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
        if slow > 3:  # анимация растянута больше чем втрое — картинка подолгу стоит: в сцену нужны события под речь
            print(f"  ⚠ {scene}: картинка стоит — речь в {slow:.1f} раза длиннее анимации; добавьте событий под фразы", flush=True)

    if a.voice_only:
        print("Озвучка готова — дальше раскадровка: uv run python core/pipeline/animatic.py " + a.paper)
        return
    lst = vdir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = VIDEOS / slug / f"{slug}_{a.engine}.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)])
    print(f"Готово: {final} ({duration(final):.0f} с)")
    # ворота 2 и 3 (законы 27, 30, 31): тон на концах фраз и журналы кадров (опоздание кадра > 0,5 с, наложения)
    import speech_check
    res, _ = speech_check.report(paper)
    bad_tone = {c: b for c, (n, b, _) in res.items() if n and len(b) / n > speech_check.BAD_SHARE}
    issues = []
    fdir = VIDEOS / slug / "frame_check"
    for scene in nar.ORDER:
        f = fdir / f"{scene}.json"
        if a.voice_only or not f.exists():
            continue
        d = json.loads(f.read_text())
        late = [(k, round(tf - ts, 1)) for k, tf, ts in d.get("sync", []) if tf - ts > 0.5]
        if late:
            issues.append(f"{scene}: кадр опоздал " + ", ".join(f"фраза {k} на {x} с" for k, x in late))
        if d.get("problems"):
            issues.append(f"{scene}: наложений в кадрах {len(d['problems'])} (videos/{slug}/frame_check/{scene}.json)")
    for c, b in bad_tone.items():
        issues.append(f"{c}: подъём тона на конце фраз " + ", ".join(f"{k} (+{st})" for k, st in b) + " — speech_check.py --reroll 2")
    if issues:
        print("Ворота после сборки — нужно поправить:")
        for x in issues:
            print("  ✗", x)


if __name__ == "__main__":
    main()
