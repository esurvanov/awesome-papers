"""Озвучка голосами OpenAI с приёмами для естественной русской речи (по ветке форума OpenAI про русский голос):
  • подробная инструкция голосу по схеме «голос, подача, интонация, темп, паузы, ударения» (VOICE_STYLE);
  • расстановка ударений и буквы «ё» программой RUAccent (stress) — знак ударения U+0301 после гласной;
  • движки OpenAI: синтезатор речи (audio/speech), разговорная модель (chat), живая модель (realtime по websocket);
  • локальный русский голос Silero (silero) — без интернета и ключей; запасной: xenia без разметки ударений + чистка CLEAN[1].
Голос по умолчанию — DEFAULT: живая модель OpenAI gpt-realtime-2.1, голос verse (выбран автором на слух 21.10.2026 из 10 голосов;
Silero всех версий — «стальной, нет объёма»). Указание голосу — блоки VOICE_PARTS (voice_style), затем VERBATIM;
закреплены автором 21.10.2026 после правок «твёрже, без смягчения», «чётче акценты», «конец фразы вниз». Не менять без нового образца.
Используется сборщиком core/pipeline/build.py и для образцов голоса (core/pipeline/voice_samples.py)."""
import base64
import re
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # корень репозитория

# голос по умолчанию для всех роликов (см. описание модуля); ударения — знаками в тексте диктора, RUAccent поверх них не запускается
DEFAULT = {"engine": "realtime", "model": "gpt-realtime-2.1", "voice": "verse",
           "wpm": 0}  # 0 — темп не трогать: понравившийся образец звучит ~100 слов/мин как есть

# Указание голосу — из блоков. Порядок блоков = порядок строк в указании. Для другого ролика или манеры меняется отдельный блок:
#   voice_style(tempo="Темп: спокойный, примерно 110 слов в минуту.")  или  VOICE_OVERRIDE = {...} в narration.py статьи.
# Блоки по умолчанию закреплены автором на слух 21.10.2026 (образец
# videos/2502.13266-rubik/voice_samples/verse_hard/6_ИК1_вниз_с_английским.wav); не менять без нового образца и сверки на слух.
VOICE_PARTS = {
    "voice": "Голос: носитель русского языка, обычное московское произношение.",
    "register": "Регистр: разговорный, уверенный — как толковый рассказчик в научно-популярном ролике. "
                "Без пафоса, без восклицаний, без восхищения.",
    "rhythm": "Ритм и ударения: чёткий ритм русской речи — ударные слоги ясные, упругие, заметно сильнее безударных; "
              "безударные гласные короткие, с редукцией. Ни одного «размазанного» слова.",
    "phrase": "Фраза: делится на смысловые куски по 3–6 слов; в каждом куске один главный акцент на ключевом слове "
              "(числа, названия, новые понятия — всегда с акцентом). Конец утверждения — твёрдо вниз, без зависания и без подъёма.",
    "tempo": "Темп: живой, примерно 130 слов в минуту; паузы короткие, на точках чуть длиннее.",
    "delivery": "Подача: собранно, деловито, ясная громкая артикуляция. Без улыбки в голосе, без придыхания, без мягкости.",
    "consonants": "Произношение согласных: строго твёрдо. Не смягчай согласные, которые в русском твёрдые: «т», «д», «н», «л», «с», «з», «р» "
                  "перед а, о, у, ы, э и на конце слова звучат твёрдо, без мягкого призвука («ход», а не «хьодь»; «лабиринт», а не «льабиринть»).\n"
                  "Мягко звучат только те согласные, что стоят перед е, ё, и, ю, я или мягким знаком. Никакого иностранного акцента.",
    "stress": "Ударения: строго по знакам ударения в тексте; буква ё всегда звучит как «ё».",
    "intonation": "Интонация: повествовательная (ИК-1) во всех фразах. Тон падает на ударном слоге последнего значимого слова "
                  "и остаётся низким до конца — голосом ставится точка.\n"
                  "Никаких подъёмов тона в конце слов, смысловых кусков и предложений. Перед запятой и тире — ровно или вниз, не вверх. "
                  "Подъём тона — только в настоящем вопросе (со знаком «?»).",
    # служебный дубль по-английски: модели OpenAI внимательнее к английским указаниям о звучании
    "intonation_en": "Intonation (important): Russian declarative intonation, IK-1. Pitch falls on the stressed syllable of the last key word "
                     "and stays low. Every statement ends firmly DOWN. Never rising at phrase ends, no uptalk, no question-like or "
                     "'to be continued' rises before commas or dashes. Rising pitch only in real questions.",
}


def voice_style(**override):
    """Указание голосу из блоков VOICE_PARTS; override заменяет блоки по имени, пустая строка убирает блок, новое имя — добавляет в конец."""
    unknown = set(override) - set(VOICE_PARTS)
    parts = {**VOICE_PARTS, **override}
    if unknown:
        print(f"  указание голосу: новые блоки {sorted(unknown)} — в конец", flush=True)
    return "\n".join(v for v in parts.values() if v)


VOICE_STYLE = voice_style()

VERBATIM = " Прочитай текст пользователя вслух дословно, ничего не добавляя, не пропуская и не комментируя."

_acc = None

# поправки поверх RUAccent: (что заменить, на что) — после разметки ударений
STRESS_FIX = [
    ("два шага́", "два ша́га"), ("три шага́", "три ша́га"), ("четыре шага́", "четы́ре ша́га"), ("четы́ре шага́", "четы́ре ша́га"),
    ("два́ шага́", "два ша́га"), ("три́ шага́", "три ша́га"),
]


def stress(text):
    """Ударения и ё (RUAccent): «+» перед ударной гласной → знак ударения после неё."""
    global _acc
    if _acc is None:
        from ruaccent import RUAccent
        _acc = RUAccent()
        _acc.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
    marked = []
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):  # по предложениям: сбой RUAccent на одном не валит остальные
        try:
            marked.append(_acc.process_all(sent))
        except Exception as e:
            print(f"  ударения: RUAccent не справился с предложением, оставляю без разметки ({type(e).__name__})", flush=True)
            marked.append(sent)
    marked = " ".join(marked)
    out, i = [], 0
    while i < len(marked):
        if marked[i] == "+" and i + 1 < len(marked):
            out.append(marked[i + 1] + "́")
            i += 2
        else:
            out.append(marked[i])
            i += 1
    res = "".join(out)
    for a, b in STRESS_FIX:
        res = res.replace(a, b)
    return res


def openai_key():
    for line in (ROOT / ".env.local").read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("В .env.local нет OPENAI_API_KEY")


def _post(url, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {openai_key()}", "Content-Type": "application/json"})
    for attempt in range(1, 5):  # запрос иногда зависает — ждём ограниченно и повторяем
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            print(f"  запрос к OpenAI: попытка {attempt} не удалась ({e})", flush=True)
            if attempt == 4:
                raise
            time.sleep(5 * attempt)


def speech(text, model, voice, style=VOICE_STYLE):
    """Синтезатор речи. Возвращает WAV."""
    return _post("https://api.openai.com/v1/audio/speech",
                 {"model": model, "voice": voice, "input": text, "response_format": "wav", "instructions": style})


def chat_audio(text, model, voice, style=VOICE_STYLE):
    """Разговорная модель, просим читать дословно. Возвращает WAV."""
    d = json.loads(_post("https://api.openai.com/v1/chat/completions", {
        "model": model, "modalities": ["text", "audio"], "audio": {"voice": voice, "format": "wav"},
        "messages": [{"role": "system", "content": style + VERBATIM}, {"role": "user", "content": text}]}))
    return base64.b64decode(d["choices"][0]["message"]["audio"]["data"])


def realtime_audio(text, model, voice, style=VOICE_STYLE):
    """Живая модель по websocket. Возвращает WAV (PCM 24 кГц моно)."""
    import asyncio
    import io
    import wave
    import websockets

    async def run():
        url = f"wss://api.openai.com/v1/realtime?model={model}"
        async with websockets.connect(url, additional_headers={"Authorization": f"Bearer {openai_key()}"}, max_size=None) as ws:
            await ws.send(json.dumps({"type": "session.update", "session": {
                "type": "realtime", "instructions": style + VERBATIM, "output_modalities": ["audio"],
                "audio": {"output": {"voice": voice, "format": {"type": "audio/pcm", "rate": 24000}}}}}))
            await ws.send(json.dumps({"type": "conversation.item.create", "item": {
                "type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]}}))
            await ws.send(json.dumps({"type": "response.create"}))
            pcm = bytearray()
            while True:
                ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=120))
                t = ev.get("type", "")
                if t in ("response.output_audio.delta", "response.audio.delta"):
                    pcm += base64.b64decode(ev["delta"])
                elif t == "response.done":
                    break
                elif t == "error":
                    raise RuntimeError(ev.get("error"))
            return bytes(pcm)

    pcm = asyncio.run(run())
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000), w.writeframes(pcm)
    return buf.getvalue()


_silero = None

# чистка голоса Silero от «песка» вокодера: уровни выбираются на слух (образцы — voice_samples.py --clean)
CLEAN = {
    0: "",
    1: "deesser=i=0.5:m=0.5:f=0.5",                                                  # только шипящие
    2: "deesser=i=0.6:m=0.6:f=0.5,lowpass=f=11000,afftdn=nr=8:nf=-45",              # шипящие + верхний «песок»
    3: "deesser=i=0.8:m=0.7:f=0.5,lowpass=f=9500,afftdn=nr=14:nf=-40",              # сильная чистка (может глушить)
}


# как произносить латинские названия (Silero читает только кириллицу)
SAY_LATIN = {"OpenAI": "Оупен Эй Ай", "ChatGPT": "Чат Джи Пи Ти", "GAP": "Гэп", "Magma": "Магма", "arXiv": "Архив"}


def silero_audio(text, model="v4_ru", voice="xenia", style=None):
    """Локальный русский голос Silero: текст никуда не отправляется. Ударения — из RUAccent (знак «+» перед гласной),
    плюс собственная расстановка Silero для слов без знака. Возвращает WAV 48 кГц."""
    import io
    import re
    import torch
    import soundfile as sf
    global _silero
    if _silero is None:
        _silero, _ = torch.hub.load(repo_or_dir="snakers4/silero-models", model="silero_tts", language="ru", speaker=model, trust_repo=True)
    plus = re.sub(r"([аеёиоуыэюяАЕЁИОУЫЭЮЯ])\u0301", r"+\1", text).replace("«", "").replace("»", "")
    for lat, ru in SAY_LATIN.items():  # Silero читает только кириллицу — латиницу молча пропускает
        plus = re.sub(rf"\b{lat}\b", ru, plus)
    left = re.findall(r"[A-Za-z]{2,}", plus)
    if left:
        raise SystemExit(f"Silero не прочитает латиницу {left} — добавьте произношение в SAY_LATIN (core/pipeline/voice.py)")
    parts = []
    for sent in re.split(r"(?<=[.?!])\s+", plus.strip()):
        if sent:
            parts.append(_silero.apply_tts(text=sent, speaker=voice, sample_rate=48000, put_accent=True, put_yo=True))
            parts.append(torch.zeros(int(48000 * 0.25)))  # пауза между предложениями
    buf = io.BytesIO()
    sf.write(buf, torch.cat(parts).numpy(), 48000, format="WAV")
    return buf.getvalue()


ENGINES = {"speech": speech, "chat": chat_audio, "realtime": realtime_audio, "silero": silero_audio}

# ---- текст для голоса (PLAYBOOK, закон 33): экранный текст остаётся орфографическим, голосу — фонетическая запись трудных мест ----
# Правила — из орфоэпической нормы (Аванесов; «Русское литературное произношение»): «что», «чтобы» = [што]; «сч» в корне «счит/счёт» = [щ];
# «конечно», «скучно» = [шн]. Знак ударения при замене сохраняется. Статья может добавить свои замены: SAY_AS = {"слово": "запись"} в narration.py.
_SAY_RULES = [
    (r"(?<![а-яё])([Чч])то(?=\u0301?бы(?![а-яё]))", lambda m: ("Ш" if m.group(1) == "Ч" else "ш") + "то"),
    (r"(?<![а-яё])([Чч])то(?=\u0301?(?![а-яё]))", lambda m: ("Ш" if m.group(1) == "Ч" else "ш") + "то"),
    (r"(?<![а-яё])([Чч])то(?=-то|-нибудь)", lambda m: ("Ш" if m.group(1) == "Ч" else "ш") + "то"),
    (r"([Сс])ч(?=[иеёа]\u0301?т|ё)", lambda m: ("Щ" if m.group(1) == "С" else "щ")),
    (r"коне(\u0301?)чно", lambda m: "коне" + m.group(1) + "шно"),
    (r"ску(\u0301?)чно", lambda m: "ску" + m.group(1) + "шно"),
]


def for_voice(text, extra=None):
    """Текст для голоса: фонетическая запись трудных мест; extra — замены статьи (слово → запись)."""
    out = text
    for rx, rep in _SAY_RULES:
        out = re.sub(rx, rep, out)
    for a, b in (extra or {}).items():
        out = re.sub(r"(?<![а-яё\u0301])" + re.escape(a) + r"(?![а-яё])", b, out)
    return out
