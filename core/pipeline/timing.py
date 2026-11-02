"""Время фраз диктора по настоящей записи: где в озвучке начинается каждая фраза сцены.

Фразы разделены паузами. Находим паузы (ffmpeg silencedetect, локально — ничего никуда не отправляется) и берём столько самых длинных,
сколько стыков между фразами; их концы по порядку — начала фраз. Если пауз меньше, чем стыков, недостающие начала оцениваются
по доле букв текста (так считалось раньше). Используется сценами (story.beat), листом сверки (sync_sheet) и раскадровкой (animatic).
Запуск для проверки: uv run python core/pipeline/timing.py videos/<папка>/audio/A05.realtime.wav 5"""
import re
import subprocess
import sys

__all__ = ["sentences", "audio_length", "phrase_starts"]


def sentences(text):
    """Фразы текста диктора — по точке, вопросу, восклицанию; знаки ударения убраны."""
    plain = text.replace("́", "")
    return [s for s in re.split(r"(?<=[.?!])\s+", plain.strip()) if s]


def audio_length(wav):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def _silences(wav, noise_db=-32, min_len=0.12):
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(wav), "-af", f"silencedetect=noise={noise_db}dB:d={min_len}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends))


def phrase_starts(wav, text):
    """Начала фраз (секунды от начала записи) и длина записи. Первая фраза — с начала речи.
    Для каждого стыка фраз берётся пауза рядом с оценкой по доле букв (±3 с): длиннее — лучше, дальше от оценки — хуже.
    Самая длинная пауза в сцене может стоять внутри фразы (после тире, перед формулой), поэтому одна длина паузы не годится."""
    sents = sentences(text)
    length = audio_length(wav)
    sil = _silences(wav)
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0       # тишина в самом начале записи
    inner = [(a, b) for a, b in sil if a > lead + 0.3 and b < length - 0.3]
    plain = " ".join(sents)
    pos, est = 0, []
    for s_ in sents:
        est.append(lead + pos / len(plain) * (length - lead))
        pos += len(s_) + 1
    out, last = [lead], lead
    for e in est[1:]:
        near = [(a, b) for a, b in inner if abs(b - e) <= 3.0 and b > last + 0.5]
        if near:
            a, b = max(near, key=lambda x: (x[1] - x[0]) - 0.15 * abs(x[1] - e))
            out.append(b)
        else:
            out.append(max(e, last + 0.5))
        last = out[-1]
    return out, length


if __name__ == "__main__":
    wav, n = sys.argv[1], int(sys.argv[2])
    starts, length = phrase_starts(wav, " ".join(["фраза."] * n))
    print(f"длина {length:.1f} с; начала фраз: " + ", ".join(f"{t:.1f}" for t in starts))
