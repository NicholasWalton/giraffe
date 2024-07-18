import pytest

from chapter1 import URL
from chapter2 import Browser

LINE_WIDTH_IN_CHARACTERS = 800 // 13 - 1
ORIGIN = [13.0, 18.0]


@pytest.fixture
def browser():
    url = URL("data:text/html,AB" + " " * (LINE_WIDTH_IN_CHARACTERS - 2) + "C")
    browser = Browser()
    browser.load(url)
    return browser


def test_text_displayed(browser):
    # while browser.window.dooneevent(ALL_EVENTS | DONT_WAIT):
    #     pass
    assert browser.window.children == {'!canvas': browser.canvas}
    assert browser.canvas.itemcget('A', 'text') == 'A'


def test_text_marches(browser):
    assert browser.canvas.coords('A') == ORIGIN
    assert browser.canvas.coords('B') == [26.0, ORIGIN[1]]


def test_text_wraps(browser):
    assert browser.canvas.coords('C') == [ORIGIN[0], 36.0]
