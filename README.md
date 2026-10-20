# awesome-papers

Ролики по свежим научным статьям «простыми словами»: анимация на [ManimGL](https://github.com/3b1b/manim)
(библиотека 3Blue1Brown, форк в `vendor/manim`), русский голос, автоматическая сборка и проверки сценария.

## 🧩 Устройство

| Часть | Где | Что |
|---|---|---|
| ⚙️ **Ядро** | `core/`, `PLAYBOOK.md` | общее для всех роликов: стиль и значки, полоса «мы здесь», сборка с голосом, проверка законов сценария, шаблон статьи, инструкция |
| 📄 **Статьи** | `papers/<arxiv-id>-<слово>/` | прикладное: паспорт ролика, текст диктора, сцены, сценарий, данные, `NOTES.md` |
| 🎞 Форк ManimGL | `vendor/manim/` | правки движка — `vendor/manim/UPSTREAM.md` |
| 🚫 Не в git | `videos/`, `.env.local` | кадры, озвучка, готовые ролики; ключ OpenAI |

## 🎬 Ролики

| Статья | Папка | Паспорт |
|---|---|---|
| 2610.23637 · разрыв соотношений (Бартольди, Бридсон, Михайлов, Николсон) | `papers/2610.23637-relation-gap` | ✅ |
| 2610.22161 · склейка слабой аппроксимируемости (Pat Lank) | `papers/2610.22161-weak-approx` | — |
| 2610.22128 · реликтовое излучение и G | `papers/2610.22128-cmb` | — |
| 2610.00011 · модель спинового стекла | `papers/2610.00011-spin-glass` | — |

## 🚀 Быстрый старт

```bash
uv sync                                                                          # Python 3.12, всё в .venv
uv run python core/pipeline/check_passport.py papers/2610.23637-relation-gap     # законы сценария
uv run python core/pipeline/build.py papers/2610.23637-relation-gap              # ролик с голосом → videos/
uv run manimgl papers/2610.23637-relation-gap/scenes.py A04 -s -w --video_dir videos/frames   # кадр одной сцены
```

Нужны `uv` и `ffmpeg`. Голос по умолчанию — локальный Silero (бесплатно, без интернета); голоса OpenAI — ключ
`OPENAI_API_KEY` в `.env.local`.

## ➕ Новый ролик

```bash
cp -R core/templates/paper papers/<arxiv-id>-<слово>
```

Дальше — по `PLAYBOOK.md`: разбор статьи → паспорт → сверка с автором → сцены → проверка → голос на слух → сборка.
Ролики — локальные файлы; в git только код, тексты и данные.
