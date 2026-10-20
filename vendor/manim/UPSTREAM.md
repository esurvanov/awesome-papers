# Форк ManimGL

Исходники https://github.com/3b1b/manim, скопированы с коммита
`fafa083a4fb274bba9cabde0b6e2f50ba6da0622` (ветка master от 9 сентября 2026; номер версии в коде 1.7.2, но код
новее одноимённого релиза на PyPI — отрисовка через wgpu).

Правим здесь по необходимости. Каждую правку относительно upstream
записываем ниже: файл и зачем.

## Наши правки

- `setup.cfg`: добавлен `av` в `install_requires` — `manimlib` импортирует его
  (`mobject/types/video_mobject.py`), а upstream объявил его только в
  `requirements.txt`; без него `import manimlib` падает.
