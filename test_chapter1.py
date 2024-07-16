import pathlib
from io import StringIO

import pytest

import chapter1
from chapter1 import URL

EMPTY_HTML = "<!doctype html>\r\n<html>\r\n</html>\r\n"

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


def test_build_request(example_url):
    expected_request = '\r\n'.join((
        "GET /index.html HTTP/1.1",
        "Host: example.org",
        "Connection: close",
        "User-Agent: giraffe",
        "\r\n",
    ))
    assert example_url._build_request() == expected_request


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
    _ = example_url._parse_statusline(fake_response)
    headers = example_url._parse_headers(fake_response)

    assert headers["content-type"] == "text/html; charset=UTF-8"


def test_parse_response(example_url, fake_response):
    assert example_url._parse_response(fake_response) == EMPTY_HTML


def test_show_empty(example_url):
    assert example_url.show(EMPTY_HTML) == "\r\n\r\n\r\n"


def test_show_content(example_url):
    assert example_url.show("<html><body>content</body></html>") == "content"


def test_https_default_port():
    url = URL("https://example.org/index.html")
    assert url.port == 443


def test_custom_port():
    url = URL("https://example.org:8080")
    assert url.port == 8080


def test_file_scheme(tmp_path):
    tmp_file = tmp_path / "example.html"
    expected_response = EMPTY_HTML.encode('utf-8')
    tmp_file.write_bytes(expected_response)
    file_url = URL(f"file://{tmp_file}")
    assert f'{file_url.scheme.name}://{file_url.path}' == tmp_file.as_uri()
    assert file_url.request() == EMPTY_HTML


def test_default_page():
    url = URL(chapter1.DEFAULT_PAGE)
    body = url.request()
    assert body == pathlib.Path("./example1-simple.html").read_text()
    assert url.load().strip() == "This is a simple\n    web page with some\n    text in it."
