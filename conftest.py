import pytest

import chapter2
from chapter1 import URL

SCROLL_AMOUNT = 10
ORIGIN = (13, 18)


@pytest.fixture
def sample_url():
    return URL("data:text/html,A B <b>bold</b>")


@pytest.fixture
def browser(sample_url):
    browser = chapter2.HeadlessBrowser()
    browser.load(sample_url)
    return browser
