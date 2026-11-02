"""Проверка озвучки по спецификации чтения (PLAYBOOK, закон 27): куда идёт тон на конце каждой фразы.

Для повествовательной фразы (точка) тон на конце должен падать (ИК-1); подъём больше порога — брак. Для вопроса (знак «?») подъём допустим.
Измерение локальное (автокорреляционный F0, ffmpeg silencedetect), ничего никуда не отправляется. Границы фраз — по паузам записи (timing.py).
Запуск (из корня):
    uv run python core/pipeline/speech_check.py papers/<папка>                  # отчёт по всем сценам
    uv run python core/pipeline/speech_check.py papers/<папка> --reroll 2       # пересинтезировать сцены с долей брака > 20% (до 2 попыток, лучшая остаётся)
Пороги рабочие (литературные цифры не найдены — см. PLAYBOOK, «Голос»): подъём > 1,5 полутона = брак; доля брака в сцене > 20% = пересинтез."""
import argparse
import importlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from timing import phrase_starts  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RISE_ST, BAD_SHARE = 1.5, 0.20


def f0(x, sr, fmin=70, fmax=300, hop=0.01, win=0.04):
    n, h, out = int(win * sr), int(hop * sr), []
    for i in range(0, len(x) - n, h):
        f = x[i:i + n] * np.hanning(n)
        if np.sqrt((f ** 2).mean()) < 0.01:
            out.append(np.nan)
            continue
        ac = np.correlate(f, f, "full")[n - 1:]
        ac /= ac[0] + 1e-9
        lo, hi = int(sr / fmax), int(sr / fmin)
        k = lo + np.argmax(ac[lo:hi])
        out.append(sr / k if ac[k] > 0.5 else np.nan)
    return np.array(out)


def _sentences(text):
    plain = text.replace("́", "")
    return [s for s in re.split(r"(?<=[.?!])\s+", plain.strip()) if s]


def measure(wav, text):
    """[(номер фразы, знак конца, изменение тона на конце в полутонах или None)] для записи сцены."""
    x, sr = sf.read(str(wav))
    x = x if x.ndim == 1 else x[:, 0]
    sents = _sentences(text)
    starts, length = phrase_starts(wav, text)
    sil = subprocess.run(["ffmpeg", "-v", "info", "-i", str(wav), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sstart = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", sil)]
    send = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", sil)]
    F = f0(x, sr)
    out = []
    for i, s in enumerate(sents):
        nxt = starts[i + 1] if i + 1 < len(starts) else length
        cand = [a for a, b in zip(sstart, send) if abs(b - nxt) < 0.05 and a < nxt]
        t_end = cand[0] if cand else (nxt - 0.3 if i + 1 < len(starts) else length)
        j = int(t_end / 0.01)
        seg = F[max(0, j - 40):j]
        seg = seg[~np.isnan(seg)]
        if len(seg) < 12:
            out.append((i + 1, s[-1], None))
            continue
        a, b = np.median(seg[:len(seg) // 2]), np.median(seg[-len(seg) // 3:])
        out.append((i + 1, s[-1], round(float(12 * np.log2(b / a)), 1)))
    return out


def report(paper, scenes=None):
    sys.path.insert(0, str(paper))
    nar = importlib.import_module("narration")
    audio = ROOT / "videos" / paper.name / "audio"
    res = {}
    for code in nar.ORDER:
        if scenes and code not in scenes:
            continue
        wav = audio / f"{code}.realtime.wav"
        if not wav.exists():
            continue
        m = measure(wav, nar.TEXT[code])
        decl = [(k, e, st) for k, e, st in m if e != "?" and st is not None]
        bad = [(k, st) for k, e, st in decl if st > RISE_ST]
        res[code] = (len(decl), bad, m)
    return res, nar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("--reroll", type=int, default=0)
    a = ap.parse_args()
    paper = Path(a.paper).resolve()
    res, nar = report(paper)
    tot = sum(n for n, _, _ in res.values())
    bad = sum(len(b) for _, b, _ in res.values())
    print(f"повествовательных фраз {tot}, с подъёмом на конце > {RISE_ST} пт: {bad} ({100 * bad / max(tot, 1):.0f}%)")
    worst = []
    for code, (n, b, _) in res.items():
        if n and len(b) / n > BAD_SHARE:
            worst.append(code)
        if b:
            print(f"  {code}: " + ", ".join(f"фраза {k} (+{st})" for k, st in b))
    if a.reroll and worst:
        audio = ROOT / "videos" / paper.name / "audio"
        for code in worst:
            best = len(res[code][1])
            keep = audio / f"{code}.realtime.wav"
            for attempt in range(a.reroll):
                bak = audio / f"{code}.best.wav"
                shutil.copy(keep, bak)
                for ext in ("hash",):
                    p = audio / f"{code}.realtime.{ext}"
                    if p.exists():
                        p.unlink()
                keep.unlink()
                subprocess.run(["uv", "run", "python", str(ROOT / "core/pipeline/build.py"), str(paper), "--voice-only", "--only", code], cwd=ROOT, check=False)
                if not keep.exists():
                    shutil.move(bak, keep)
                    break
                r, _ = report(paper, [code])
                now = len(r[code][1])
                print(f"  {code}: попытка {attempt + 1}: брак было {best}, стало {now}")
                if now < best:
                    best = now
                    bak.unlink()
                else:
                    shutil.move(bak, keep)
                if best == 0:
                    break


if __name__ == "__main__":
    main()
