# awesome-papers

Ролики по свежим научным статьям «простыми словами»: анимация на [ManimGL](https://github.com/3b1b/manim)
(библиотека 3Blue1Brown, форк в `vendor/manim`), русский голос, автоматическая сборка и проверки сценария.

## 🧩 Устройство

| Часть | Где | Что |
|---|---|---|
| ⚙️ **Ядро** | `core/`, `PLAYBOOK.md` | общее для всех роликов: стиль и значки, полоса «мы здесь», сборка с голосом, проверка законов сценария, шаблон статьи, инструкция |
| 📄 **Статьи** | `papers/<arxiv-id>-<слово>/` | прикладное: паспорт ролика, текст диктора, сцены, сценарий, данные, `NOTES.md` |
| 🎞 Форк ManimGL | `vendor/manim/` | правки движка — `vendor/manim/UPSTREAM.md` |
| ✏️ Animator | `vendor/Animator/` | вложенный репозиторий — форк [Animator](https://github.com/ashishjamarkattel/Animator): ролики «рисованная доска» по одной фразе |
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
git clone --recurse-submodules https://github.com/esurvanov/awesome-papers   # вместе с vendor/Animator
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

## 📜 Сторонний код

| Что | Откуда | Лицензия | Как подключено |
|---|---|---|---|
| ManimGL | [3b1b/manim](https://github.com/3b1b/manim), © 3Blue1Brown LLC | MIT (`vendor/manim/LICENSE.md`) | копия исходников с правками (`vendor/manim/UPSTREAM.md`) |
| Animator | [ashishjamarkattel/Animator](https://github.com/ashishjamarkattel/Animator), автор — Ashish Jamarkattel | **не указана** — лицензия запрошена у автора | вложенный репозиторий: форк [esurvanov/Animator](https://github.com/esurvanov/Animator); код в этот репозиторий не копируется |
| Детектор текста CRAFT (внутри Animator, `animator/models/craft.onnx`) | [clovaai/CRAFT-pytorch](https://github.com/clovaai/CRAFT-pytorch), NAVER Corp. | код — MIT; лицензия весов не указана | в составе форка Animator |

Пока у Animator нет лицензии, его код живёт только в форке на GitHub (форк публичных репозиториев разрешён правилами
GitHub); переносить его исходники в этот репозиторий — после того как автор добавит лицензию.
