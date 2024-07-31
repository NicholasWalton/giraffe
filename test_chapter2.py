import tkinter

import pytest

import chapter2
from chapter1 import URL, Text, Tag

HSTEP, VSTEP = 17, 23
SCROLL_AMOUNT = 10
ORIGIN = (13, 18)
LINE_HEIGHT = 1.25 * VSTEP


@pytest.fixture
def sample_url():
    return URL("data:text/html,A B <b>bold</b>")


@pytest.fixture
def browser(sample_url):
    browser = chapter2.HeadlessBrowser()
    browser.load(sample_url)
    return browser


def assert_text_location(entry, expected_location, expected_text):
    actual_location, actual_text, _ = entry
    assert (actual_location, actual_text) == (expected_location, expected_text)


def test_tk_browser(sample_url):
    browser = chapter2.Browser()
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


def test_text_marches():
    layout = chapter2.Layout([Text("A B")])
    assert_text_location(layout[0], ORIGIN, 'A')
    assert_text_location(layout[1], (ORIGIN[0] + 2 * HSTEP, ORIGIN[1]), 'B')


def test_text_wraps():
    characters_to_fill_line = (800 - ORIGIN[0]) // HSTEP - 1
    layout = chapter2.Layout([Text("A" * characters_to_fill_line + " " + "C")])
    assert_text_location(layout[-1], (ORIGIN[0], ORIGIN[1] + LINE_HEIGHT), 'C')


def test_scroll_down(browser):
    assert browser.scroll == 0
    browser.scroll_down(None)
    assert browser.scroll == SCROLL_AMOUNT


def test_scroll_up(browser):
    assert browser.scroll == 0
    browser.scroll = SCROLL_AMOUNT
    browser.scroll_up(None)
    assert browser.scroll == 0


def test_scroll_wheel(browser):
    expected = 123
    assert browser.scroll == 0

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
    scroll = chapter2.VMARGIN + 1
    browser.scroll = scroll
    assert browser._is_offscreen(0)
    assert not browser._is_offscreen(1)  # only bottom pixel will be visible
    assert not browser._is_offscreen(chapter2.HEIGHT + scroll)  # only top pixel will be visible
    assert browser._is_offscreen(chapter2.HEIGHT + scroll + 1)


def test_newline():
    layout = chapter2.Layout([Text("A"), Tag("br"), Text("\n\nC")])
    assert_text_location(layout[1], (ORIGIN[0], ORIGIN[1] + 1.5 * VSTEP), 'C')


def test_resize(browser):
    expected_text = 'B'
    assert_text_location(browser.display_list[1], (ORIGIN[0] + 2 * HSTEP, ORIGIN[1]), expected_text)

    class MockEvent:
        def __init__(self):
            self.width = 3 * HSTEP  # one character wide plus margins
            self.height = 400

    browser.resize(MockEvent())
    assert_text_location(browser.display_list[1], (ORIGIN[0], ORIGIN[1] + LINE_HEIGHT), expected_text)
    assert browser.height == 400


def test_layout_bold():
    layout = chapter2.Layout([Tag("b"), Text("bolded"), Tag("/b"), Text("normal")])
    _, text, font = layout[0]
    assert font == chapter2.FakeFont(weight="bold")
    _, text, font = layout[1]
    assert font == chapter2.FakeFont(weight="normal")
