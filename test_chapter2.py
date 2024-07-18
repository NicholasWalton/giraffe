import pytest

import chapter2
from chapter1 import URL
from chapter2 import Browser

SCROLL_AMOUNT = 10

LINE_WIDTH_IN_CHARACTERS = 800 // 13 - 1
ORIGIN = (13.0, 18.0)


# while browser.window.dooneevent(ALL_EVENTS | DONT_WAIT):
#     print('.')

@pytest.fixture
def browser():
    url = URL("data:text/html,A")
    browser = Browser()
    browser.load(url)
    return browser


@pytest.fixture
def layout():
    return chapter2.layout("AB" + " " * (LINE_WIDTH_IN_CHARACTERS - 2) + "C")


def test_text_displayed(browser):
    assert browser.window.children == {'!canvas': browser.canvas}
    assert browser.canvas.itemcget('A', 'text') == 'A'


def test_text_marches(layout):
    assert layout[0] == (ORIGIN, 'A')
    assert layout[1] == ((26.0, ORIGIN[1]), 'B')


def test_text_wraps(layout):
    assert layout[-1] == ((ORIGIN[0], 36.0), 'C')


def test_scrolled(browser):
    assert browser.scroll == 0
    browser.scroll = SCROLL_AMOUNT
    browser.draw()
    assert browser.canvas.coords('A') == [ORIGIN[0], ORIGIN[1] - SCROLL_AMOUNT]


def test_scroll_down(browser):
    assert browser.scroll == 0
    assert "scroll_down" in browser.window.bind('<Down>')  # Not ideal but Tkinter is not test-friendly
    browser.scroll_down(None)
    assert browser.scroll == SCROLL_AMOUNT


def test_scroll_up(browser):
    assert browser.scroll == 0
    assert "scroll_up" in browser.window.bind('<Up>')  # Not ideal but Tkinter is not test-friendly
    browser.scroll = SCROLL_AMOUNT
    browser.scroll_up(None)
    assert browser.scroll == 0


def test_scroll_wheel(browser):
    expected = 123
    assert browser.scroll == 0
    assert "scroll_wheel" in browser.window.bind('<MouseWheel>')  # Not ideal but Tkinter is not test-friendly

    class MockEvent:
        def __init__(self):
            self.delta = expected

    browser.scroll_wheel(MockEvent())
    assert browser.scroll == expected


def test_scroll_off_top(browser):
    assert browser.scroll == 0
    browser.scroll_up(None)
    assert browser.scroll == 0


def test_skip_offscreen(browser):
    scroll = 19.0
    browser.scroll = scroll
    assert browser._is_offscreen(0)
    assert not browser._is_offscreen(1)  # only bottom pixel will be visible
    assert not browser._is_offscreen(chapter2.HEIGHT + scroll)  # only top pixel will be visible
    assert browser._is_offscreen(chapter2.HEIGHT + scroll + 1)


def test_newline():
    layout = chapter2.layout("\nC")
    assert layout[0] == ((ORIGIN[0], 45.0), 'C')
