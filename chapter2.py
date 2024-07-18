import tkinter

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
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)

    def load(self, url):
        text = url.load()
        display_list = layout(text)
        for (x, y), c in display_list:
            self.canvas.create_text(x, y, tags=c, text=c)


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append(((cursor_x, cursor_y), c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


if __name__ == '__main__':
    main()
