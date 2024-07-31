import tkinter

from giraffe.url import Text, Tag
from conftest import SCROLL_AMOUNT, ORIGIN
from giraffe.browser import Browser, Layout, FakeFont


def test_tk_browser(sample_url):
    browser = Browser()
    browser.load(sample_url)

    ## text_displayed
    assert browser.window.children == {'!canvas': browser.canvas}
    assert browser.canvas.itemcget('A', 'text') == 'A'
    actual_font_name = browser.canvas.itemcget('bold', 'font')
    actual_font = tkinter.font.Font(name=actual_font_name, exists=True)
    assert actual_font.cget("weight") == "bold"

    ## bindings
    assert "scroll_down" in browser.window.bind('<Down>')  # Not ideal but Tkinter is not test-friendly
    assert "scroll_up" in browser.window.bind('<Up>')  # Not ideal but Tkinter is not test-friendly
    assert "scroll_wheel" in browser.window.bind('<MouseWheel>')  # Not ideal but Tkinter is not test-friendly
    assert "resize" in browser.window.bind('<Configure>')  # Not ideal but Tkinter is not test-friendly

    ## scrolled
    assert browser.scroll == 0
    browser.scroll = SCROLL_AMOUNT
    browser.draw()
    assert browser.canvas.coords('A') == [ORIGIN[0], ORIGIN[1] - SCROLL_AMOUNT]

    # while browser.window.dooneevent(ALL_EVENTS | DONT_WAIT):
    #     print('.')


def test_layout_bold():
    layout = Layout([Tag("b"), Text("bolded"), Tag("/b"), Text("normal")])
    _, text, font = layout[0]
    assert font == FakeFont(weight="bold")
    _, text, font = layout[1]
    assert font == FakeFont(weight="normal")


def test_layout_italic():
    layout = Layout([Tag("i"), Text("italic"), Tag("/i"), Text("normal")])
    _, text, font = layout[0]
    assert font == FakeFont(slant="italic")
    _, text, font = layout[1]
    assert font == FakeFont()


def test_end_tag_in_attribute():
    layout = Layout([Tag("style"), Tag('a href="/style"'), Text("css"), Tag("/style")])
    assert len(layout) == 0
