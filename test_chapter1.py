import pytest

from chapter1 import URL
from io import StringIO

SAMPLE_HTTP_RESPONSE = """HTTP/1.0 200 OK
Content-Type: text/html; charset=UTF-8
Connection: close

<!doctype html>
<html>
</html>
"""


def test_host():
    url = URL("http://example.org/")
    assert url.host == "example.org"


def test_host_no_slash():
    url = URL("http://example.org")
    assert url.host == "example.org"


def test_url_path():
    url = URL("http://example.org/my/path")
    assert url.path == "/my/path"


def test_build_request():
    url = URL("http://example.org/index.html/")
    assert url._build_request() == "GET /index.html/ HTTP/1.0\r\nHost: example.org\r\n\r\n"


@pytest.fixture()
def example_url():
    return URL("http://example.org/index.html")


@pytest.fixture
def fake_response():
    return StringIO(SAMPLE_HTTP_RESPONSE, newline="\r\n")


def test_parse_statusline(example_url, fake_response):
    version, status, explanation = example_url._parse_statusline(fake_response)
    assert version == "HTTP/1.0"
    assert status == "200"
    assert explanation == "OK\r\n"


def test_parse_headers(example_url, fake_response):
    fake_response.readline()  # skip status line
    headers = example_url._parse_headers(fake_response)

    assert headers["content-type"] == "text/html; charset=UTF-8"


def test_parse_response(example_url, fake_response):
    assert example_url._parse_response(fake_response) == "<!doctype html>\r\n<html>\r\n</html>\r\n"
