import chapter2
from chapter1 import Text, Tag
from conftest import ORIGIN, SCROLL_AMOUNT

HSTEP, VSTEP = 17, 23
LINE_HEIGHT = 1.25 * VSTEP


def assert_text_location(entry, expected_location, expected_text):
    actual_location, actual_text, _ = entry
    assert (actual_location, actual_text) == (expected_location, expected_text)


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
