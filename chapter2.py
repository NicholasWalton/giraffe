import logging
import time
import tkinter
import tkinter.font
from dataclasses import dataclass
from tkinter import BOTH
from typing import override

from chapter1 import URL, Text

NORMAL = "normal"

WIDTH, HEIGHT = 800, 600
HMARGIN, VMARGIN = 13, 18


def main():
    logging.basicConfig(level=logging.INFO)
    import sys
    browser = Browser()
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("https://browser.engineering/examples/xiyouji.html")
    browser.load(url)
    browser.canvas.pack()
    tkinter.mainloop()


@dataclass
class FakeFont:
    HSTEP, VSTEP = 17, 23
    weight: str = "normal"
    @staticmethod
    def metrics(name):
        match name:
            case "linespace":
                return FakeFont.VSTEP
            case _:
                raise ValueError()

    @staticmethod
    def measure(word):
        return FakeFont.HSTEP * len(word)


class HeadlessBrowser:
    def __init__(self):
        self.height = HEIGHT
        self.display_list = []
        self.scroll = 0
        self.fonts = FakeFont

    def load(self, url):
        self.text = url.load()
        self.display_list = Layout(self.text, self.fonts)
        self.draw()

    def draw(self):
        words = 0
        frame_start = time.perf_counter()
        for (x, y), word, font in self.display_list:
            if not self._is_offscreen(y):
                logging.debug(f"Drawing [{word}] at {x},{y}")
                self.create_text(x, y - self.scroll, word, font)
                words += 1
        frame_end = time.perf_counter()
        frame_ms = (frame_end - frame_start) * 1000
        logging.info(f"Drew {words} words in {frame_ms:.1f} ms")

    def create_text(self, x, y, word, font):
        logging.debug(f"Pretending to draw [{word}] in {font} at {x},{y}")

    def _should_draw(self, y):
        return not self._is_offscreen(y)

    def _is_offscreen(self, y):
        return (self.scroll + self.height) < y or y < (self.scroll - VMARGIN)

    def scroll_down(self, _):
        self._scroll(10)

    def scroll_up(self, _):
        self._scroll(-10)

    def scroll_wheel(self, event):
        self._scroll(event.delta)

    def _scroll(self, amount):
        self.scroll += amount
        self.scroll = max(0, self.scroll)
        self.draw()

    def resize(self, event):
        self.height = event.height
        self.display_list = Layout(self.text, self.fonts, event.width)
        self.draw()


class Browser(HeadlessBrowser):
    def __init__(self):
        super().__init__()
        self.window = tkinter.Tk()
        self.fonts = tkinter.font.Font
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=self.height)
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<MouseWheel>", self.scroll_wheel)
        self.window.bind("<Configure>", self.resize)
        self.canvas.pack(fill=BOTH, expand=1)

    @override
    def draw(self):
        self.canvas.delete("all")
        super().draw()

    @override
    def create_text(self, x, y, word, font):
        escaped = word.replace('"', '\\"')
        self.canvas.create_text(x, y, text=word, font=font, anchor='nw', tag=f'"{escaped}"')


class Layout(list):
    def __init__(self, tokens, fonts=FakeFont, width=WIDTH):
        self.cursor_x, self.cursor_y = HMARGIN, VMARGIN
        self.fonts = fonts
        self.width = width
        self.weight = NORMAL
        self.in_script = False
        self.in_style = False
        for token in tokens:
            if isinstance(token, Text):
                if not self.in_script and not self.in_style:
                    self._layout_text(token.text)
            elif "/script" in token.tag:
                self.in_script = False
            elif token.tag.startswith("script"):
                self.in_script = True
            elif "/style" in token.tag:
                self.in_style = False
            elif token.tag.startswith("style"):
                self.in_style = True
            elif token.tag in ("br","/p","/li","/div"):
                if self.cursor_x != HMARGIN:
                    self.cursor_x = HMARGIN
                    self.cursor_y += 1.5 * self._font().metrics("linespace")
            elif token.tag == "b":
                self.weight = "bold"
            elif token.tag == "/b":
                self.weight = NORMAL

    def _layout_text(self, text):
        for word in text.split():
            self._layout_word(word)

    def _layout_word(self, word):
        w = self._font().measure(word)
        if self.cursor_x + w > self.width - HMARGIN:
            self.cursor_y += 1.25 * self._font().metrics("linespace")
            self.cursor_x = HMARGIN
        self.append(((self.cursor_x, self.cursor_y), word, self._font()))
        self.cursor_x += w + self._font().measure(" ")
    
    def _font(self):
        return self.fonts(weight = self.weight)


if __name__ == '__main__':
    main()
