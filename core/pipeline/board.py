"""Сцена «доской»: кадр сцены ManimGL рисуется «от руки» локальным движком Animator (vendor/Animator, форк) под голос диктора.

Запуск (из корня):
    uv run python core/pipeline/board.py papers/<папка> A03            # голос по умолчанию (voice.DEFAULT)
    uv run python core/pipeline/board.py papers/<папка> A03 --dark     # тёмная доска (мел), без перекраски
Результат — videos/<папка>/board/<сцена>.mp4 (в git не попадает).

Что делает:
  1. рендерит последний кадр сцены с BOARD_PLAN — manimkit.story_base записывает, где лежит каждый объект и когда он появился;
  2. перекрашивает тёмный кадр в светлую доску: светлота каждого пикселя переворачивается, оттенок и насыщенность сохраняются
     (белый текст → чёрный, голубой → синий), фон — чисто белый;
  3. озвучивает текст сцены (кэш по тексту и настройкам голоса);
  4. собирает разметку Animator: объект = область, порядок и окно рисования — из времени появления в сцене, растянутого на речь;
  5. запускает Animator из его окружения (vendor/Animator/.venv) — Gemini не нужен, код Animator в этот репозиторий не копируется.
Окружение Animator (один раз): cd vendor/Animator && uv venv --python 3.12 .venv &&
    uv pip install --python .venv/bin/python numpy opencv-python-headless scikit-image scipy Pillow onnxruntime pydantic"""
import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ANIMATOR = ROOT / "vendor" / "Animator"
MIN_DRAW = 0.6  # секунд: меньше окно рисования на глаз не читается


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def duration(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout)


def to_board(src, dst):
    """Тёмный кадр → светлая доска: rgb + (1 − max − min) переворачивает светлоту, не трогая оттенок и насыщенность."""
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
    out = a + (1 - a.max(axis=2, keepdims=True) - a.min(axis=2, keepdims=True))
    out[out.min(axis=2) > 0.9] = 1.0  # бывший фон и его шум — чисто белый
    Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8)).save(dst)


def narrate(text, wav, style=None):
    """Озвучка голосом по умолчанию; кэш — по тексту и настройкам голоса."""
    d = voice.DEFAULT
    style = style or voice.VOICE_STYLE
    h = hashlib.sha1(f"{d}|{style}|{voice.VERBATIM}|{text}".encode()).hexdigest()
    tag = wav.with_suffix(".hash")
    if wav.exists() and tag.exists() and tag.read_text() == h:
        return
    raw = wav.with_suffix(".raw.wav")
    raw.write_bytes(voice.ENGINES[d["engine"]](text, d["model"], d["voice"], style=style))
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1", str(wav)])
    raw.unlink()
    tag.write_text(h)


def region_plan(meta, speech, idea):
    """Объекты сцены → разметка Animator: порядок появления и окно рисования на шкале речи."""
    items = sorted(meta["items"], key=lambda it: it["start"])
    # на кадре остаются не все объекты сцены (часть уходит раньше) — шкала от первого оставшегося до конца сцены
    first = items[0]["start"] if items else 0.0
    k = speech * 0.9 / max(meta["duration"] - first, 1e-6)  # последние 10 % речи кадр уже готов
    regions, windows = [], []
    for i, it in enumerate(items, 1):
        b = it["box"]
        if b["xmax"] - b["xmin"] < 2 or b["ymax"] - b["ymin"] < 2:
            continue
        t0 = (it["start"] - first) * k
        regions.append({"label": f"object_{i}", "role": "main_concept", "reveal_order": len(regions) + 1, "box": b,
                        "expected_visual": "часть кадра сцены", "reveal": "stroke", "beat": len(regions) + 1})
        windows.append([round(t0, 2), round(max((it["end"] - first) * k, t0 + MIN_DRAW), 2)])
    return {"idea": idea, "regions": regions, "beat_windows": windows}


def hand_overlay(video, scene_file, layer, cues, text, speech, lead, workdir, quality="high"):
    """Рисунок «от руки» поверх готовой сцены, в её же тёмном стиле.
    layer — сцена-слой (в том же файле сцен), где по порядку добавлены только части рисунка в координатах сцены;
    cues — по слову озвучки на каждую часть: часть рисуется с момента, когда диктор произносит это слово.
    Как: кадр слоя → светлая доска → Animator рисует части в своих окнах → обратно в тёмный (светлота переворачивается
    тем же преобразованием) → чёрное прозрачно → поверх сцены. Возвращает путь к новому видео."""
    workdir.mkdir(parents=True, exist_ok=True)
    objs = workdir / f"{layer}.objects.json"
    sh(["manimgl", str(scene_file), layer, "-s", "-w", "--video_dir", str(workdir / "frames")], cwd=ROOT,
       env=dict(os.environ, SLOW="1", BOARD_PLAN=str(objs)))
    img = workdir / f"{layer}_board.png"
    to_board(workdir / "frames" / f"{layer}.png", img)
    items = json.loads(objs.read_text())["items"]
    if len(items) != len(cues):
        raise SystemExit(f"{layer}: частей рисунка {len(items)}, слов-сигналов {len(cues)} — должно совпадать")
    vlen = duration(video)
    regions, windows = [], []
    for i, (it, word) in enumerate(zip(items, cues), 1):
        if word not in text:
            raise SystemExit(f"{layer}: слова-сигнала «{word}» нет в тексте сцены")
        t0 = lead + text.index(word) / len(text) * speech  # время слова ≈ доля символов до него
        regions.append({"label": f"part_{i}", "role": "main_concept", "reveal_order": i, "beat": i, "reveal": "stroke",
                        "box": it["box"], "expected_visual": word})
        windows.append([round(t0, 2), round(min(t0 + 1.6, vlen), 2)])  # дольше 1,6 с Animator часть не рисует
    plan = workdir / f"{layer}.regions.json"
    plan.write_text(json.dumps({"idea": layer, "regions": regions, "beat_windows": windows}, ensure_ascii=False))
    anim = workdir / f"{layer}_hand.mp4"
    py = ANIMATOR / ".venv" / "bin" / "python"
    sh([str(py), "-m", "animator", str(img), "-o", str(anim), "--duration", f"{vlen:.3f}", "--regions", str(plan),
        "--quality", quality], cwd=ANIMATOR)
    out = video.with_name(video.stem + ".hand.mp4")
    w, h = sh(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0",
               str(video)]).stdout.strip().split(",")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(anim), "-filter_complex",
        f"[1]scale={w}:{h},fps=30,negate,hue=h=180,colorkey=black:0.25:0.1[a];[0][a]overlay=eof_action=repeat[v]",
        "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(out)])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("scene")
    ap.add_argument("--dark", action="store_true", help="не перекрашивать: тёмная доска, «мел»")
    ap.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    a = ap.parse_args()
    paper = (ROOT / a.paper).resolve()
    out = ROOT / "videos" / paper.name / "board"
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    text = nar.TEXT[a.scene]

    plan_raw = out / f"{a.scene}.objects.json"
    env = dict(os.environ, SLOW="1", BOARD_PLAN=str(plan_raw))
    sh(["manimgl", str(paper / getattr(nar, "SCENE_FILE", "scenes.py")), a.scene, "-s", "-w", "--video_dir", str(out / "frames")],
       cwd=ROOT, env=env)
    frame = out / "frames" / f"{a.scene}.png"
    img = out / f"{a.scene}.png"
    if a.dark:
        Image.open(frame).convert("RGB").save(img)
    else:
        to_board(frame, img)

    wav = out / f"{a.scene}.wav"
    narrate(text, wav, voice.voice_style(**getattr(nar, "VOICE_OVERRIDE", {})))
    plan = out / f"{a.scene}.regions.json"
    plan.write_text(json.dumps(region_plan(json.loads(plan_raw.read_text()), duration(wav), a.scene), ensure_ascii=False, indent=1))

    mp4 = out / f"{a.scene}.mp4"
    py = ANIMATOR / ".venv" / "bin" / "python"
    if not py.exists():
        raise SystemExit("нет окружения Animator — команда в описании модуля")
    sh([str(py), "-m", "animator", str(img), "-o", str(mp4), "--audio", str(wav), "--regions", str(plan), "--quality", a.quality],
       cwd=ANIMATOR)
    print(f"Готово: {mp4} ({duration(mp4):.1f} с)")


if __name__ == "__main__":
    main()
