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
        # self.canvas.create_rectangle(10, 20, 400, 300)
        # self.canvas.create_oval(100, 100, 150, 150)
        # self.canvas.create_text(200, 150, text="Hi!")
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in url.load():
            self.canvas.create_text(cursor_x, cursor_y, tags=c, text=c)
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP


if __name__ == '__main__':
    main()
