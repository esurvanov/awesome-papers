"""Памятка в начале сессии (хук SessionStart в .claude/settings.json): обязательные ворота и где что лежит.
Только чтение; ничего не меняет. Печатает коротко — это попадает в контекст сессии."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
pb = (ROOT / "PLAYBOOK.md").read_text(encoding="utf-8")
laws = re.findall(r"^\| (\d+) \| \S+ \*\*([^*\n]+)\*\*", pb, flags=re.M)
hist = [int(x) for x in re.findall(r"^\| (\d+) \| «", pb, flags=re.M)]
papers = sorted(p.name for p in (ROOT / "papers").iterdir() if p.is_dir() and not p.name.startswith("."))
print("Ролики «простыми словами»: флоу — навык film (.claude/skills/film), правила — PLAYBOOK.md "
      f"(законов {len({n for n, _ in laws})}, последнее замечание автора № {max(hist) if hist else 0}).")
print("Обязательно: автор оценивает результат, частности решаешь сам; перед переделкой — первопричины агентами (.claude/agents);"
      " новое правило → PLAYBOOK + программная проверка.")
print("Ворота: check_passport.py → text_check.py (ударения по реестру core/lang, обыденная лексика, текст на слух) → озвучка →"
      " speech_check.py (тон вниз) → сцены на core/manimkit/film.py → build.py (опоздание кадра > 0,5 с, наложения — ошибка).")
seen = {}
for n, t in laws:
    seen.setdefault(int(n), t)
print("Законы 22+: " + "; ".join(f"{n} {t}" for n, t in sorted(seen.items()) if n >= 22))
print("Ролики: " + ", ".join(papers))
