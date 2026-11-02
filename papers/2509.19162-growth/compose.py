"""Сборка сцены фильма: 3D-видео Blender + прозрачный слой подписей ManimGL + голос (с тишиной LEAD в начале).
Запуск (из корня): uv run python papers/2509.19162-growth/compose.py A01 [A04 …]  →  videos/2509.19162-growth/film/<сцена>.mp4
Весь фильм из готовых сцен: uv run python papers/2509.19162-growth/compose.py --all"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
FILM = ROOT / "videos" / HERE.name / "film"
AUDIO = ROOT / "videos" / HERE.name / "audio"
LEAD = 0.4


def sh(cmd):
    subprocess.run(cmd, check=True, cwd=ROOT)


def overlay(code):
    sh(["uv", "run", "manimgl", str(HERE / "overlays.py"), code, "-w", "-t", "--video_dir", str(FILM / "overlay")])
    return next((FILM / "overlay").rglob(f"{code}.mov"))


def compose(code):
    base, over, wav = FILM / f"{code}_3d.mp4", overlay(code), AUDIO / f"{code}.realtime.wav"
    out = FILM / f"{code}.mp4"
    d = int(LEAD * 1000)
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(base), "-i", str(over), "-i", str(wav), "-filter_complex",
        f"[0:v]scale=1920:1080:flags=lanczos[b];[1:v]scale=1920:1080[o];[b][o]overlay=0:0:shortest=0[v];[2:a]adelay={d}|{d},apad[a]",
        "-map", "[v]", "-map", "[a]", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", str(out)])
    print(f"{code}: {out}")
    return out


def still_background(code, image, zoom=0.06, blur=6):
    """Фон 2D-сцены: неподвижный кадр станции, размытый, с медленным наездом — вместо 3D-рендера (карточка, обзор)."""
    wav = AUDIO / f"{code}.realtime.wav"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                               capture_output=True, text=True).stdout) + LEAD + 0.8
    n = int(dur * 24)
    sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(image), "-vf",
        f"scale=1920:1080,zoompan=z='1+{zoom}*on/{n}':d={n}:s=1920x1080:fps=24,gblur=sigma={blur},eq=brightness=-0.08",
        "-t", f"{dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(FILM / f"{code}_3d.mp4")])


def ambient_background(code, k, blur=5):
    """Фон сцены с инфографикой: кусок общего облёта станции (AMB_3d.mp4, 120 с), у каждой сцены — своё место облёта."""
    wav = AUDIO / f"{code}.realtime.wav"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                               capture_output=True, text=True).stdout) + LEAD + 0.8
    start = (k * 37.0) % max(1.0, 120.0 - dur)
    sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-i", str(FILM / "AMB_3d.mp4"), "-t", f"{dur:.2f}", "-vf",
        f"scale=1920:1080:flags=lanczos,gblur=sigma={blur},eq=brightness=-0.05", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(FILM / f"{code}_3d.mp4")])


BOARD = ["A07", "A08", "A09", "A10", "A11", "A12", "A13", "A14", "A15",
         "F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "A16"]


if __name__ == "__main__":
    codes = sys.argv[1:]
    if codes and codes[0] == "--still":  # фон 2D-сцен из образцового кадра: compose.py --still A02 A03
        img = ROOT / "videos" / HERE.name / "film" / "look" / "A01_2.png"
        for c in codes[1:]:
            still_background(c, img)
            compose(c)
        raise SystemExit
    if codes and codes[0] == "--ambient":  # сцены с инфографикой поверх облёта: compose.py --ambient [A07 …]
        for c in codes[1:] or BOARD:
            ambient_background(c, BOARD.index(c))
            compose(c)
        raise SystemExit
    if codes == ["--all"]:
        sys.path.insert(0, str(HERE))
        import narration as N
        parts = [FILM / f"{c}.mp4" for c in N.ORDER if (FILM / f"{c}.mp4").exists()]
        lst = FILM / "list.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
        sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(FILM / f"{HERE.name}_film.mp4")])
        print(f"фильм: {len(parts)} сцен → {FILM / (HERE.name + '_film.mp4')}")
    else:
        for c in codes:
            compose(c)
