"""Простая зарисовка (без хорошей графики) сцен 2–3 фильма «Сорок столов»/«Тринадцатидолье»:
слово-карточку кладут на все тринадцать столов, на двух оно сливается с другим словом — столы гаснут;
Нулевой стол (оригинал) стоит первым. Запуск из корня: uv run manimgl papers/ega1-film/sketch.py Sketch -w -l --video_dir videos/ega1-film/sketch"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(d for d in HERE.parents if (d / "pyproject.toml").exists())
sys.path.insert(0, str(ROOT / "core"))
from manimlib import *
from manimkit import *

VALLEYS = ["Ур", "Таш", "Сайма", "Кора", "Вель", "Инги", "Дарн", "Хо", "Лазет", "Мирт", "Эшан", "Циб", "Ору"]
BAD = {"Эшан", "Дарн"}


def table(label, w=0.78, h=0.5, zero=False):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.08)
    if zero:
        r.set_stroke(C_YEL, 2).set_fill(C_YEL, 0.08)
    else:
        r.set_stroke(C_GREY, 2).set_fill(WHITE, 0.06)
    t = tx(label, 16, C_YEL if zero else WHITE).next_to(r, DOWN, buff=0.1)
    return VGroup(r, t)


class Sketch(Base):
    def construct(self):
        # счётчики
        counter = tx("подписано столов 0 / 13", 26, WHITE).to_corner(UL, buff=0.4)
        days = tx("до подписания 6 дней", 26, C_YEL).to_corner(UR, buff=0.4)
        self.play(FadeIn(counter), FadeIn(days))

        # зал: Нулевой стол первым, затем тринадцать
        tables = VGroup(table("Нулевой", zero=True), *[table(v) for v in VALLEYS]).arrange(RIGHT, buff=0.18)
        tables.set_width(13.2).move_to(DOWN * 0.6)
        hall = tx("Зал Тринадцати Столов. Оригинал — на Нулевом столе, без номера, первым", 24, C_GREY).to_edge(DOWN, buff=0.5)
        self.play(LaggedStartMap(FadeIn, tables, shift=UP * 0.2, lag_ratio=0.06), run_time=2.5)
        self.play(FadeIn(hall))
        self.wait(2)

        # слово-карточка
        self.play(FadeOut(hall))
        word = tx("неприкосновенность", 30, WHITE)
        card = VGroup(RoundedRectangle(width=word.get_width() + 0.5, height=0.7, corner_radius=0.12).set_stroke(C_BLUE, 2).set_fill(C_BLUE, 0.15), word)
        card.move_to(UP * 1.9)
        cap1 = tx("Одно слово кладут на все столы сразу", 24, C_GREY).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(card, shift=DOWN * 0.3), FadeIn(cap1))
        self.wait(1)

        copies = VGroup()
        for tb in tables[1:]:
            c = card.copy().set_width(tb[0].get_width() * 0.92).move_to(tb[0])
            copies.add(c)
        self.play(LaggedStart(*[TransformFromCopy(card, c) for c in copies], lag_ratio=0.08), run_time=3)
        self.wait(1)

        # на двух столах слово сливается с другим: столы гаснут
        cap2 = tx("На двух столах у него нет своего слова: оно совпадает с «безнаказанность»", 24, C_GREY).to_edge(DOWN, buff=0.5)
        self.play(FadeOut(cap1), FadeIn(cap2))
        dims = []
        for tb, c in zip(tables[1:], copies):
            if tb[1].text in BAD:
                other = tx("безнаказанность", 30, C_RED)
                bad = VGroup(RoundedRectangle(width=other.get_width() + 0.5, height=0.7, corner_radius=0.12).set_stroke(C_RED, 2).set_fill(C_RED, 0.2), other)
                bad.set_width(c.get_width()).move_to(c)
                dims.append(ReplacementTransform(c, bad))
                dims.append(tb[0].animate.set_stroke(C_RED, 3).set_fill(C_RED, 0.12))
                dims.append(tb[1].animate.set_color(C_RED))
        self.play(*dims, run_time=1.5)
        self.wait(1.5)

        # замкнутое множество: обвести оба
        bad_tables = VGroup(*[tb for tb in tables[1:] if tb[1].text in BAD])
        loops = VGroup(*[SurroundingRectangle(tb, color=C_RED, buff=0.12).set_stroke(C_RED, 2) for tb in bad_tables])
        cap3 = tx("Столы, где слово гаснет, — короткий список. Расстояний между столами нет: есть только это", 24, C_GREY).to_edge(DOWN, buff=0.5)
        self.play(FadeOut(cap2), FadeIn(cap3), ShowCreation(loops))
        self.wait(2.5)

        # Нулевой стол: верно почти везде
        self.play(FadeOut(card), FadeOut(loops))
        glow = SurroundingRectangle(tables[0], color=C_YEL, buff=0.12).set_stroke(C_YEL, 3)
        q = tx("Советник: «В оригинале всё ясно. Подписываем?»", 26, WHITE).move_to(UP * 2.1)
        self.play(FadeOut(cap3), FadeIn(q), ShowCreation(glow))
        self.wait(2)
        a = tx("Толмач: «Что верно на Нулевом столе, верно на всех — кроме двух. Их и проверяем»", 26, C_YEL).move_to(UP * 1.4)
        self.play(FadeIn(a))
        arrows = VGroup(*[Arrow(tables[0].get_top() + UP * 0.05, tb.get_top() + UP * 0.05, buff=0.05, path_arc=-0.6).set_stroke(C_RED, 3) for tb in bad_tables])
        self.play(ShowCreation(arrows), run_time=1.5)
        self.wait(2)

        # счётчик задачи
        new_counter = tx("проверить столов 2 / 13", 26, C_GREEN).to_corner(UL, buff=0.4)
        self.play(FadeOut(counter), FadeIn(new_counter))
        self.wait(1.5)

        # крючок
        self.play(FadeOut(q), FadeOut(a), FadeOut(arrows), FadeOut(glow))
        hook = tx("Список на амнистию при чтении Эшана. Третья строка — убийца её брата.", 28, C_RED).move_to(UP * 1.8)
        self.play(FadeIn(hook))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self.frame])
        end = tx("Конец зарисовки · сцены 2–3", 30, C_GREY)
        self.play(FadeIn(end))
        self.wait(1.5)
