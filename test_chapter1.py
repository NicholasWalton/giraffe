import pathlib
from io import BytesIO

import pytest

import giraffe
from giraffe.url import URL, parse_entity, TooManyRedirects, Tag, Text

EMPTY_HTML = "<!doctype html>\r\n<html>\r\n</html>\r\n"
EXAMPLE_URL = "http://example.org/index.html"
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
    expected_request = "\r\n".join(
        (
            "GET /index.html HTTP/1.0",
            "Host: example.org",
            "User-Agent: giraffe",
            "\r\n",
        )
    )
    assert example_url._build_request() == expected_request


@pytest.fixture()
def example_url():
    return URL(EXAMPLE_URL)


@pytest.fixture
def fake_response():
    return _encode_string_as_http_response(SAMPLE_HTTP_RESPONSE)


def _encode_string_as_http_response(string):
    return BytesIO(string.replace('\n', '\r\n').encode("utf-8"))


def test_parse_statusline(example_url, fake_response):
    version, status, explanation = example_url._parse_statusline(fake_response)
    assert version == "HTTP/1.0"
    assert status == "200"
    assert explanation == "OK\r\n"


def test_parse_headers(example_url, fake_response):
    _ = example_url._parse_statusline(fake_response)
    example_url._parse_headers(fake_response)

    assert example_url._headers["content-type"] == "text/html; charset=UTF-8"


def test_parse_response(example_url, fake_response):
    _ = example_url._parse_statusline(fake_response)
    example_url._parse_headers(fake_response)
    assert example_url._parse_body(fake_response) == EMPTY_HTML


def test_show_empty(example_url):
    assert example_url.lex(EMPTY_HTML) == [Tag("!doctype html"), Text("\r\n"), Tag("html"), Text("\r\n"), Tag("/html"),
                                           Text("\r\n")]


def test_show_content(example_url):
    assert example_url.lex("<html><body>content</body></html>") == [Tag("html"), Tag("body"), Text("content"),
                                                                    Tag("/body"), Tag("/html")]


def test_https_default_port():
    url = URL("https://example.org/index.html")
    assert url.port == 443


def test_custom_port():
    url = URL("https://example.org:8080")
    assert url.port == 8080


def test_file_scheme(tmp_path):
    tmp_file = tmp_path / "example.html"
    expected_response = EMPTY_HTML.encode("utf-8")
    tmp_file.write_bytes(expected_response)
    if str(tmp_file).startswith("/"):
        file_url = URL(f"file://{tmp_file}")
    else:
        file_url = URL(f"file:///{tmp_file}")
    assert f"{file_url.scheme.name}://{file_url.path}" == tmp_file.as_uri()
    assert file_url.request() == EMPTY_HTML


def test_file_scheme_osx():
    file_url = URL("file:///Users/league/giraffe/example1-simple.html")
    assert file_url.path == "/Users/league/giraffe/example1-simple.html"


def test_default_page():
    url = URL(giraffe.url.DEFAULT_PAGE)
    body = url.request()
    assert body == pathlib.Path("./example1-simple.html").read_text()
    assert (
            giraffe.url.strip_tags(url.load()).strip()
            == "This is a simple\n    web page with some\n    text in it."
    )


def test_data_scheme():
    url = URL("data:text/html,Hello world!")
    assert url.load() == [Text("Hello world!")]


def test_entities():
    assert parse_entity("&lt;") == "<"
    assert parse_entity("&gt;") == ">"
    assert parse_entity("&unknown;") == "&unknown;"


def test_entities_in_html():
    url = URL("data:text/html,<http>hello &lt;&unknown;&gt;</http>")
    assert url.load() == [Tag("http"), Text("hello <&unknown;>"), Tag("/http")]


def test_long_tag():
    url = URL(
        'data:text/html,<img height="1" width="1" style="display:none" alt="fbpx" src="https://www.facebook.com/tr?id=1218016184890789&ev=PageView&noscript=1"/>')
    actual, = url.load()
    assert isinstance(actual, Tag)


def test_view_source():
    url = URL("view-source:" + giraffe.url.DEFAULT_PAGE)
    assert url.load() == [Text(pathlib.Path("./example1-simple.html").read_text())]


def test_keep_alive(example_url):
    KEEP_ALIVE_HTTP_RESPONSE = """HTTP/1.0 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 12

0123456789
noise
"""
    fake_response = _encode_string_as_http_response(KEEP_ALIVE_HTTP_RESPONSE)
    _ = example_url._parse_statusline(fake_response)
    example_url._parse_headers(fake_response)
    assert example_url._headers["content-length"] == "12"
    body = example_url._parse_body(fake_response)
    assert body == "0123456789\r\n"


def test_no_redirect(example_url, fake_response):
    assert not example_url._redirect(fake_response)
    assert example_url._redirect_count == 0


def test_redirect(example_url):
    expected_path = "/local_mirror/redirect.html"
    fake_response = _redirect(f"file://{expected_path}")
    assert example_url.path != expected_path

    assert example_url._redirect(fake_response)
    assert example_url.path == expected_path
    assert example_url.scheme == giraffe.url.Scheme.file
    assert example_url._redirect_count == 1


def test_relative_redirect(example_url):
    expected_path = "/redirect.html"
    fake_response = _redirect(expected_path)
    assert example_url.path != expected_path
    assert example_url._redirect(fake_response)
    assert example_url.path == expected_path


def test_too_many_redirects():
    fake_response = _redirect("/")
    max_redirects = 10
    example_url = URL(EXAMPLE_URL, max_redirects - 1)
    with pytest.raises(TooManyRedirects):
        example_url._redirect(fake_response)


def _redirect(location):
    return _encode_string_as_http_response(f"""HTTP/1.0 399 Some kind of redirect
Location: {location}

""")
