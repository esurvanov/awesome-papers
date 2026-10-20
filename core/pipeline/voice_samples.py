"""Образцы голоса для выбора на слух: длинный кусок (~40–60 с) из текста диктора статьи, несколько голосов.
Запуск (из корня):
    uv run python core/pipeline/voice_samples.py papers/<папка> A05 A10            # голоса Silero (бесплатно, на Маке)
    uv run python core/pipeline/voice_samples.py papers/<папка> A05 A10 --openai   # плюс голоса OpenAI (нужны ключ и согласие)
Образцы — videos/<папка>/voice_samples/. Выбирает автор на слух; см. раздел «Голос» в PLAYBOOK.md."""
import argparse
import importlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from voice import ENGINES, CLEAN, stress  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

SILERO = [("silero_xenia", "silero", "v4_ru", "xenia", False), ("silero_baya", "silero", "v4_ru", "baya", False),
          ("silero_aidar", "silero", "v4_ru", "aidar", False), ("silero_eugene", "silero", "v4_ru", "eugene", False)]
OPENAI = [("openai_realtime_cedar", "realtime", "gpt-realtime-2.1", "cedar", True),
          ("openai_chat_marin", "chat", "gpt-audio-1.5", "marin", True),
          ("openai_tts_cedar", "speech", "gpt-4o-mini-tts-2025-03-20", "cedar", True)]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("scenes", nargs="+", help="коды сцен, текст которых озвучить подряд (лучше с числами и терминами)")
    ap.add_argument("--openai", action="store_true")
    a = ap.parse_args()
    paper = (ROOT / a.paper).resolve()
    sys.path.insert(0, str(paper))
    text = " ".join(importlib.import_module("narration").TEXT[c] for c in a.scenes)
    out = ROOT / "videos" / paper.name / "voice_samples"
    out.mkdir(parents=True, exist_ok=True)
    for name, eng, model, voice, st in SILERO + (OPENAI if a.openai else []):
        try:
            raw = out / f"{name}.raw.wav"
            raw.write_bytes(ENGINES[eng](stress(text) if st else text, model, voice))
            chain = ",".join(x for x in (CLEAN[1] if eng == "silero" else "", "loudnorm=I=-16:TP=-1.5:LRA=11") if x)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", chain, "-ar", "48000", "-ac", "1", str(out / f"{name}.wav")], check=True)
            raw.unlink()
            print(name, "готов", flush=True)
        except Exception as e:  # noqa: BLE001
            print(name, "ошибка:", e, flush=True)
    print("Образцы:", out)
