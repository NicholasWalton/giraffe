import pytest

import chapter2
from chapter1 import URL
from chapter2 import Browser

LINE_WIDTH_IN_CHARACTERS = 800 // 13 - 1
ORIGIN = (13.0, 18.0)


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
    # while browser.window.dooneevent(ALL_EVENTS | DONT_WAIT):
    #     pass
    assert browser.window.children == {'!canvas': browser.canvas}
    assert browser.canvas.itemcget('A', 'text') == 'A'


def test_text_marches(layout):
    assert layout[0] == (ORIGIN, 'A')
    assert layout[1] == ((26.0, ORIGIN[1]), 'B')


def test_text_wraps(layout):
    assert layout[-1] == ((ORIGIN[0], 36.0), 'C')
