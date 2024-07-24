import logging
import time
import tkinter
import tkinter.font
from tkinter import BOTH
from typing import override

from chapter1 import URL, Text

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18


def main():
    logging.basicConfig(level=logging.DEBUG)
    import sys
    browser = Browser()
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("https://browser.engineering/examples/xiyouji.html")
    browser.load(url)
    browser.canvas.pack()
    tkinter.mainloop()


class FakeFont:
    @staticmethod
    def metrics(name):
        match name:
            case "linespace":
                return VSTEP
            case _:
                raise ValueError()

    @staticmethod
    def measure(word):
        return HSTEP * len(word)


class HeadlessBrowser:
    def __init__(self):
        self.height = HEIGHT
        self.display_list = []
        self.scroll = 0
        self.font = FakeFont()

    def load(self, url):
        self.text = url.load()
        self.display_list = Layout(self.text, self.font)
        self.draw()

    def draw(self):
        character_count = 0
        frame_start = time.perf_counter()
        for (x, y), c in self.display_list:
            if not self._is_offscreen(y):
                self.create_text(x, y - self.scroll, c)
                character_count += 1
        frame_end = time.perf_counter()
        frame_ms = (frame_end - frame_start) * 1000
        logging.info(f"Drew {character_count} characters in {frame_ms:.1f} ms")

    def create_text(self, x, y, c):
        logging.debug(f"Pretending to draw [{c}] at {x},{y}")

    def _should_draw(self, y):
        # return self.scroll <= y + VSTEP and y <= self.scroll + HEIGHT
        return not self._is_offscreen(y)

    def _is_offscreen(self, y):
        return (self.scroll + self.height) < y or y < (self.scroll - VSTEP)

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
        self.display_list = Layout(self.text, self.font, event.width)
        self.draw()


class Browser(HeadlessBrowser):
    def __init__(self):
        super().__init__()
        self.window = tkinter.Tk()
        self.font = tkinter.font.Font()
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
    def create_text(self, x, y, c):
        self.canvas.create_text(x, y, text=c, font=self.font, anchor='nw', tag=c)


class Layout(list):
    def __init__(self, tokens, font=FakeFont(), width=WIDTH):
        cursor_x, cursor_y = HSTEP, VSTEP
        for token in tokens:
            if isinstance(token, Text):
                for line in token.text.split('\n'):
                    for word in line.split():
                        w = font.measure(word)
                        if cursor_x + w > width - HSTEP:
                            cursor_y += 1.25 * font.metrics("linespace")
                            cursor_x = HSTEP
                        self.append(((cursor_x, cursor_y), word))
                        cursor_x += w + font.measure(" ")
                    cursor_y += 1.5 * font.metrics("linespace")
                    cursor_x = HSTEP


if __name__ == '__main__':
    main()
