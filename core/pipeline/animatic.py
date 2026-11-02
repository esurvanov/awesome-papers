"""Раскадровка под голос (аниматик): черновой ролик до всякой анимации — на каждую фразу диктора карточка с тем, что будет в кадре.

Зачем: ролик целиком за минуты, без рендера сцен. На ней «новый зритель» отвечает на вопросы паспорта (VIEWER_TEST),
а автор видит, понятно ли и в каком порядке всё появляется. Время карточек — по паузам настоящей озвучки (timing.py).
Кадр фразы — схематичная картинка из videos/<папка>/storyboard/<сцена>-<N>.png (рисует storyboard.py статьи, ключ --draw),
сверху тонкой строкой — фраза диктора. Нет картинки — карточка с текстом STORYBOARD и пометкой «⚠ кадр не нарисован».

Запуск (из корня), после озвучки:
    uv run python core/pipeline/build.py papers/<папка> --voice-only
    uv run python core/pipeline/animatic.py papers/<папка>
Результат — videos/<папка>/<папка>_animatic.mp4 (в git не попадает)."""
import argparse
import importlib
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from build import LEAD, TAIL  # noqa: E402
from timing import sentences, phrase_starts  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
W, H = 1920, 1080
BG, FG, GREY = (15, 17, 21), (235, 235, 235), (139, 148, 158)


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


def card(path, head, frame, phrase, stations, active):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_head, f_frame, f_phrase, f_bar = (ImageFont.truetype(FONT, s) for s in (30, 54, 34, 22))
    d.text((60, 40), head, font=f_head, fill=GREY)
    lines = wrap(frame, f_frame, W - 240, d)
    y = H // 2 - 60 - len(lines) * 36
    for line in lines:
        d.text(((W - d.textlength(line, font=f_frame)) // 2, y), line, font=f_frame, fill=FG)
        y += 72
    py = H - 250
    for line in wrap("«" + phrase + "»", f_phrase, W - 240, d)[:3]:
        d.text(((W - d.textlength(line, font=f_phrase)) // 2, py), line, font=f_phrase, fill=GREY)
        py += 44
    xs = [120 + i * (W - 240) / max(1, len(stations) - 1) for i in range(len(stations))]
    d.line([(xs[0], H - 70), (xs[-1], H - 70)], fill=(60, 64, 70), width=2)
    for i, (x, st) in enumerate(zip(xs, stations)):
        col = FG if i == active else GREY
        r = 9 if i == active else 6
        d.ellipse([x - r, H - 70 - r, x + r, H - 70 + r], fill=col)
        d.text((x - d.textlength(st, font=f_bar) / 2, H - 52), st, font=f_bar, fill=col)
    img.save(path)


def picture_card(path, picture, head, phrase):
    """Кадр раскадровки: сверху отдельная полоса — номер и фраза диктора; под ней картинка целиком (ничего не перекрывается)."""
    strip = 120
    img = Image.new("RGB", (W, H), BG)
    pic = Image.open(picture).convert("RGB")
    ph = H - strip
    pw = int(pic.width * ph / pic.height)
    img.paste(pic.resize((pw, ph)), ((W - pw) // 2, strip))
    d = ImageDraw.Draw(img)
    f_head, f_phrase = ImageFont.truetype(FONT, 22), ImageFont.truetype(FONT, 26)
    d.text((24, 10), head, font=f_head, fill=GREY)
    for k, line in enumerate(wrap("«" + phrase + "»", f_phrase, W - 48, d)[:2]):
        d.text((24, 42 + k * 32), line, font=f_phrase, fill=FG)
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("--engine", default="realtime")
    ap.add_argument("--draw", action="store_true", help="сначала нарисовать схематичные кадры всех сцен (storyboard.py статьи)")
    a = ap.parse_args()
    paper = (ROOT / a.paper).resolve()
    sys.path.insert(0, str(paper))
    P, N = importlib.import_module("passport"), importlib.import_module("narration")
    board = getattr(P, "STORYBOARD", {})
    station = {c: st for c, st, *_ in P.SCENES}
    vdir = ROOT / "videos" / paper.name
    if a.draw:
        for scene in N.ORDER:
            subprocess.run(["manimgl", str(paper / "storyboard.py"), scene, "-s", "-w", "--video_dir", str(vdir / "storyboard" / "_render")],
                           cwd=ROOT, check=True, capture_output=True)
            print(f"{scene}: кадры нарисованы", flush=True)
        import json
        bad = {f.stem.replace(".layout", ""): json.loads(f.read_text()) for f in sorted((vdir / "storyboard").glob("*.layout.json"))}
        bad = {k: v for k, v in bad.items() if v}
        for k, v in bad.items():
            print(f"⚠ расстановка {k}: " + "; ".join(v))
        if bad:
            raise SystemExit(f"Расстановка: проблемы в {len(bad)} кадрах — поправить storyboard.py и перерисовать (--draw)")
    out_dir = vdir / "animatic"
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    for scene in N.ORDER:
        wav = vdir / "audio" / f"{scene}.{a.engine}.wav"
        if not wav.exists():
            raise SystemExit(f"{scene}: нет озвучки — сначала build.py {a.paper} --voice-only")
        sents = sentences(N.TEXT[scene])
        frames = board.get(scene, [])
        starts, speech = phrase_starts(wav, N.TEXT[scene])
        total = LEAD + speech + TAIL
        lst = out_dir / f"{scene}.txt"
        rows = []
        for k, s in enumerate(sents):
            png = out_dir / f"{scene}-{k + 1}.png"
            frame = frames[k] if k < len(frames) else "⚠ кадр не описан в STORYBOARD"
            head = f"{scene} · {station[scene]} · фраза {k + 1} из {len(sents)}"
            pic = vdir / "storyboard" / f"{scene}-{k + 1}.png"
            if pic.exists():
                picture_card(png, pic, head, s)
            else:
                card(png, head + " · ⚠ кадр не нарисован", frame, s, P.STATIONS, P.STATIONS.index(station[scene]))
            t0 = 0 if k == 0 else LEAD + starts[k]
            t1 = LEAD + starts[k + 1] if k + 1 < len(sents) else total
            rows.append(f"file '{png.name}'\nduration {t1 - t0:.3f}\n")
        lst.write_text("".join(rows) + f"file '{png.name}'\n")
        mp4 = out_dir / f"{scene}.mp4"
        delay = int(LEAD * 1000)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                        "-filter_complex", f"[1:a]adelay={delay}|{delay},apad[a]", "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
                        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-c:a", "aac", "-ar", "48000", str(mp4)], check=True)
        parts.append(mp4)
        print(f"{scene}: {len(sents)} фраз, {total:.1f} с", flush=True)
    lst = out_dir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = vdir / f"{paper.name}_animatic.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)], check=True)
    print(f"Раскадровка: {final}")


if __name__ == "__main__":
    main()
