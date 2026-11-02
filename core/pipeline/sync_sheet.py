"""Лист сверки «фраза диктора → кадр»: по каждой сцене — кадр в середине каждой фразы и сама фраза под ним.
Зачем: проверять, что всё сказанное видно на экране, и видно честно (числа — из статьи, схема подписана как схема).
Это проверка смысла — программа её не делает; лист смотрит Claude по всем сценам, затем автор.

Запуск (из корня), после сборки:
    uv run python core/pipeline/sync_sheet.py papers/<папка>            # все сцены
    uv run python core/pipeline/sync_sheet.py papers/<папка> A03 A05    # только эти
Результат — videos/<папка>/sync/<сцена>.png (в git не попадает).
Время фразы — по паузам настоящей записи (core/pipeline/timing.py), с поправкой на тишину перед речью.
Кадры — ещё и в полном размере (sync/<сцена>/фраза-N.png): обрезку и смещения видно только так."""
import argparse
import importlib
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from build import LEAD, duration  # noqa: E402
from timing import sentences, phrase_starts  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H, CAP = 640, 360, 120  # кадр в листе и высота подписи под ним


def wrap(text, font, width, draw):
    lines, cur = [], ""
    for word in text.split():
        probe = (cur + " " + word).strip()
        if draw.textlength(probe, font=font) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = probe
    return lines + [cur] if cur else lines


def sheet(scene, text, video, audio, out):
    sents = sentences(text)
    starts, speech = phrase_starts(audio, text)
    vlen = duration(video)
    full = out.with_suffix("")
    full.mkdir(exist_ok=True)
    frames = []
    for k, s in enumerate(sents):
        end = starts[k + 1] if k + 1 < len(starts) else speech
        t = min(LEAD + (starts[k] + end) / 2, vlen - 0.05)
        png = out.with_name(f"_{scene}_{len(frames)}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(full / f"фраза-{k + 1}.png")],
                       check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(full / f"фраза-{k + 1}.png"), "-vf", f"scale={W}:{H}", str(png)], check=True)
        frames.append((t, s, png))
    cols = min(3, len(frames))
    rows = (len(frames) + cols - 1) // cols
    img = Image.new("RGB", (cols * W, rows * (H + CAP)), (15, 17, 21))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 17)
    for i, (t, s, png) in enumerate(frames):
        x, y = (i % cols) * W, (i // cols) * (H + CAP)
        img.paste(Image.open(png), (x, y))
        draw.text((x + 8, y + H + 6), f"{scene} · {i + 1} · {t:.1f} с", font=font, fill=(139, 148, 158))
        for k, line in enumerate(wrap(s, font, W - 16, draw)[:4]):
            draw.text((x + 8, y + H + 28 + k * 21), line, font=font, fill=(230, 230, 230))
        png.unlink()
    img.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--engine", default="realtime", help="движок голоса, которым собран ролик (имя файлов озвучки)")
    a = ap.parse_args()
    paper = (ROOT / a.paper).resolve()
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    vid_dir, aud_dir = ROOT / "videos" / paper.name / "voiced", ROOT / "videos" / paper.name / "audio"
    out_dir = ROOT / "videos" / paper.name / "sync"
    out_dir.mkdir(parents=True, exist_ok=True)
    for scene in a.scenes or nar.ORDER:
        video, audio = vid_dir / f"{scene}.mp4", aud_dir / f"{scene}.{a.engine}.wav"
        if not video.exists() or not audio.exists():
            print(f"{scene}: нет собранной сцены или озвучки — пропуск")
            continue
        sheet(scene, nar.TEXT[scene], video, audio, out_dir / f"{scene}.png")
        print(f"{scene}: {out_dir / (scene + '.png')}")


if __name__ == "__main__":
    main()
