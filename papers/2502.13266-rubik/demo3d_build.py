"""Сборка демо 3D + доска (demo3d.py рядом): 3D-ролик → кадр застывает и плавно становится светлой доской →
поверх доски рука дорисовывает путь к выходу (Animator) → один mp4.
Запуск (из корня): uv run python papers/2502.13266-rubik/demo3d_build.py → videos/2502.13266-rubik/demo3d/demo_3d_board.mp4"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core" / "pipeline"))
from board import to_board, narrate, duration, ANIMATOR  # noqa: E402
sys.path.insert(0, str(HERE))
from demo3d import NARRATION, SEG_BASE  # noqa: E402

OUT = ROOT / "videos" / HERE.name / "demo3d"
SCENES = HERE / "demo3d.py"
FADE = 1.6   # секунд переход 3D-кадра в доску
HOLD = 1.5   # секунд держим готовый кадр после последней фразы
GAP = 0.5    # секунд тишины после каждой фразы
# часть рисунка → слово последней фразы, с которого её рисовать (Animator рисует часть ≤ 1,6 с и держит — растягивать нельзя)
DRAW_CUES = [("path", "коро́ткий"), ("start", "ста́рта"), ("exit", "вы́ходу"), ("count", "шесть")]


def sh(*cmd, **kw):
    subprocess.run([str(c) for c in cmd], check=True, capture_output=True, text=True, **kw)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # озвучка по кускам; 3D-куски растягиваются под речь, доска рисует, пока звучит последняя фраза
    wavs = [OUT / f"voice_{i}.wav" for i in range(len(NARRATION))]
    for t, w in zip(NARRATION, wavs):
        narrate(t, w)
    lens = [duration(w) + GAP for w in wavs]
    seg = [max(b, n) for b, n in zip(SEG_BASE, lens[:3])]
    draw = lens[3]
    env = dict(os.environ, DEMO_SEG=",".join(f"{x:.3f}" for x in seg))
    sh("manimgl", SCENES, "Demo3D", "-w", "--hd", "--video_dir", OUT, cwd=ROOT, env=env)
    boxes_file = OUT / "path_boxes.json"
    sh("manimgl", SCENES, "DemoPath", "-s", "-w", "--hd", "--video_dir", OUT, cwd=ROOT, env=dict(os.environ, DEMO_BOXES=str(boxes_file)))
    boxes = json.loads(boxes_file.read_text())
    clip3d = OUT / "Demo3D.mp4"
    dark, bg, path = OUT / "last_dark.png", OUT / "board_bg.png", OUT / "path_board.png"
    sh("ffmpeg", "-v", "error", "-y", "-sseof", "-0.05", "-i", clip3d, "-frames:v", "1", dark)
    to_board(dark, bg)
    to_board(OUT / "DemoPath.png", path)

    # рука рисует только путь и подписи — на белом листе; белое при умножении прозрачно
    # время слова ≈ доля символов до него во фразе × длина речи
    text = NARRATION[3]
    speech = draw - GAP
    regions, windows = [], []
    for i, (name, word) in enumerate(DRAW_CUES, 1):
        t0 = text.index(word) / len(text) * speech
        regions.append({"label": name, "role": "main_concept", "reveal_order": i, "beat": i, "reveal": "stroke",
                        "box": boxes[name], "expected_visual": name})
        windows.append([round(t0, 2), round(t0 + 1.6, 2)])
    plan = OUT / "path_regions.json"
    plan.write_text(json.dumps({"idea": "путь к выходу", "beat_windows": windows, "regions": regions}))
    anim = OUT / "path_draw.mp4"
    sh(ANIMATOR / ".venv" / "bin" / "python", "-m", "animator", path, "-o", anim, "--duration", draw, "--regions", plan,
       "--quality", "high", cwd=ANIMATOR)

    fade, over, final = OUT / "fade.mp4", OUT / "over.mp4", OUT / "demo_3d_board.mp4"  # не demo3d.mp4: на Маке совпадёт с Demo3D.mp4
    sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", FADE, "-i", dark, "-loop", "1", "-t", FADE, "-i", bg, "-filter_complex",
       f"[0]format=gbrp[a];[1]format=gbrp[b];[a][b]xfade=transition=fade:duration={FADE - 0.4}:offset=0.3,format=yuv420p", "-r", "30", fade)
    sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", bg, "-i", anim, "-filter_complex",
       f"[1]scale=1920:1080,fps=30,tpad=stop_mode=clone:stop_duration={HOLD},colorkey=white:0.3:0.15[a];[0]scale=1920:1080,fps=30[b];"
       "[b][a]overlay=shortest=1,format=yuv420p", "-r", "30", over)
    silent = OUT / "silent.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-i", clip3d, "-i", fade, "-i", over, "-filter_complex",
       "[0:v]fps=30,format=yuv420p[a];[1:v]fps=30[b];[2:v]fps=30[c];[a][b][c]concat=n=3:v=1:a=0", "-c:v", "libx264", "-crf", "18", silent)
    # фразы — с начала своих кусков: три 3D-куска, последняя — с началом рисования (после перехода в доску)
    starts = [0.0, seg[0], seg[0] + seg[1], sum(seg) + FADE]
    ins = sum((["-i", w] for w in wavs), [])
    mix = "".join(f"[{i + 1}]adelay={int(t * 1000)}:all=1[v{i}];" for i, t in enumerate(starts))
    mix += "".join(f"[v{i}]" for i in range(len(wavs))) + f"amix=inputs={len(wavs)}:normalize=0[aud]"
    sh("ffmpeg", "-v", "error", "-y", "-i", silent, *ins, "-filter_complex", mix, "-map", "0:v", "-map", "[aud]",
       "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final)
    print("Готово:", final)


if __name__ == "__main__":
    main()
