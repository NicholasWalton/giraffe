import tkinter

import pytest

from conftest import SCROLL_AMOUNT, ORIGIN
from giraffe.browser import Browser, Layout, FakeFont
from giraffe.url import Text, Tag


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
    browser.draw()
    _, original_y = browser.canvas.coords('A')
    browser.scroll = SCROLL_AMOUNT
    browser.draw()
    assert browser.canvas.coords('A') == [ORIGIN[0], original_y - SCROLL_AMOUNT]

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


@pytest.mark.parametrize("tag,size0,size1", (
        ("big", 16, 20),
        ("small", 10, 8),
))
def test_layout_size(tag, size0, size1):
    layout = Layout([Tag(tag), Text("once"), Tag(tag), Text("twice"), Tag(f"/{tag}"), Tag(f"/{tag}"), Text("normal")])
    _, text, font = layout[0]
    assert text == "once"
    assert font == FakeFont(size=size0)
    _, text, font = layout[1]
    assert text == "twice"
    assert font == FakeFont(size=size1)
    _, text, font = layout[2]
    assert text == "normal"
    assert font == FakeFont(size=12)

def test_shared_baseline():
    layout = Layout([Text("normal"), Tag("big"), Text("big")])
    (normal_x, normal_y), normal_text, normal_font = layout[0]
    (big_x, big_y), big_text, big_font = layout[1]
    assert normal_text == "normal"
    assert big_text == "big"
    assert normal_y > big_y
    