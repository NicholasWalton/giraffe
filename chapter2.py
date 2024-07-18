import logging
import time
import tkinter
from tkinter import BOTH

from chapter1 import URL

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18


def main():
    import sys
    browser = Browser()
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])
    else:
        url = URL("https://browser.engineering/examples/xiyouji.html")
    browser.load(url)
    browser.canvas.pack()
    tkinter.mainloop()


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.height = HEIGHT
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=self.height)
        self.display_list = []
        self.scroll = 0
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<MouseWheel>", self.scroll_wheel)
        self.window.bind("<Configure>", self.resize)
        self.canvas.pack(fill=BOTH, expand=1)

    def load(self, url):
        self.text = url.load()
        self.display_list = layout(self.text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        character_count = 0
        frame_start = time.perf_counter()
        for (x, y), c in self.display_list:
            if not self._is_offscreen(y):
                self.canvas.create_text(x, y - self.scroll, tags=c, text=c)
                character_count += 1
        frame_end = time.perf_counter()
        frame_ms = (frame_end - frame_start) * 1000
        logging.info(f"Drew {character_count} characters in {frame_ms} ms")

    def _should_draw(self, y):
        # return self.scroll <= y + VSTEP and y <= self.scroll + HEIGHT
        return not self._is_offscreen(y)

    def _is_offscreen(self, y):
        return y > self.scroll + self.height or y + VSTEP < self.scroll

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
        self.display_list = layout(self.text, event.width)
        self.draw()


def layout(text, width=WIDTH):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        if c == '\n':
            cursor_y += 1.5 * VSTEP
            cursor_x = HSTEP
            continue
        display_list.append(((cursor_x, cursor_y), c))
        cursor_x += HSTEP
        if cursor_x >= width - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


if __name__ == '__main__':
    main()
