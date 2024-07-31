import pytest

import giraffe
from giraffe.url import URL

SCROLL_AMOUNT = 10
ORIGIN = (13, 18)


@pytest.fixture
def sample_url():
    return URL("data:text/html,A B <b>bold</b>")


@pytest.fixture
def browser(sample_url):
    browser = giraffe.browser.HeadlessBrowser()
    browser.load(sample_url)
    return browser
