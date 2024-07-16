import pathlib
import socket
import ssl
from enum import Enum, StrEnum, auto
import sys

DEFAULT_PAGE = "file://./example1-simple.html"


class Scheme(StrEnum):
    http = auto()
    https = auto()
    file = auto()
    data = auto()

_sockets = {}

class URL:
    def __init__(self, url):
        self._headers = {}

        if url.startswith("view-source:"):
            self.renderer = SourceRenderer
        else:
            self.renderer = HtmlRenderer
        url = url.removeprefix("view-source:")
        scheme, url = url.split(":", 1)
        self.scheme = Scheme[scheme]
        if self.scheme == Scheme.http:
            self.port = 80
        elif self.scheme == Scheme.https:
            self.port = 443
        if url.startswith("//"):
            url = url.removeprefix("//")
            if "/" not in url:
                url += "/"
            authority, url = url.split("/", 1)
        match self.scheme:
            case Scheme.http | Scheme.https:
                self.host = authority
                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)
                self.path = "/" + url
                self._address = (self.host, self.port)
            case Scheme.file:
                self.path = authority + "/" + url.replace("\\", "/")
            case Scheme.data:
                self.path = url.removeprefix("text/html,")

    def request(self):
        match self.scheme:
            case Scheme.http | Scheme.https:
                response = self.get_http_response()
                content = self._parse_response(response)
            case Scheme.file:
                file_path = self.path
                with pathlib.Path(file_path).open(encoding="utf8", newline="\r\n") as f:
                    content = "".join(f.readlines())
            case Scheme.data:
                content = self.path
        return content

    def get_http_response(self):
        if (self._address, self.scheme) not in _sockets:
            print(f"Creating new socket for {self._address}", file=sys.stderr)
            new_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
            )
            new_socket.connect(self._address)
            if self.scheme == Scheme.https:
                ctx = ssl.create_default_context()
                new_socket = ctx.wrap_socket(new_socket, server_hostname=self.host)
            _sockets[self._address, self.scheme] = new_socket
        self.socket = _sockets[self._address, self.scheme]
        request = self._build_request()
        self.socket.send(request.encode("utf8"))
        response = self.socket.makefile("r", encoding="utf8", newline="\r\n")
        return response

    def _build_request(self):
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "User-Agent: giraffe\r\n"
        # request += "Connection: close\r\n"
        request += "\r\n"
        return request

    def _parse_response(self, response):
        version, status, explanation = self._parse_statusline(response)
        self._headers = self._parse_headers(response)
        content_length = int(self._headers.get("content-length", 0))
        print(f"content_length={content_length}", file=sys.stderr)
        if content_length:
            content = response.read(content_length)
            # trailing = response.read()
            # print(f"trailing:[{trailing}]", file=sys.stderr)
        else:
            content = response.read()
            self._headers["connection"] = "close"
        return content

    def _parse_statusline(self, response):
        statusline = response.readline()
        print(f"[{statusline}]", file=sys.stderr)
        return statusline.split(" ", 2)

    def _parse_headers(self, response):
        response_headers = {}

        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        return response_headers

    def load(self):
        body = self.request()
        rendered = self.show(body)
        
        if self._headers.get("connection") == "close":            
            print(f"Closing socket for {self._address}", file=sys.stderr)
            _sockets.pop((self._address, self.scheme)).close()
        else:
            print(f"Headers were [{self._headers}]", file=sys.stderr)
        return rendered


    def show(self, body):
        return self.renderer(body).render()


class SourceRenderer:
    def __init__(self, body):
        self.body = body

    def render(self):
        return self.body


class HtmlRenderer:
    def __init__(self, body):
        self.in_tag = False
        self.rendered = []
        self.entity = ""
        self.in_entity = False
        self.body = body

    def render(self):
        for c in self.body:
            if c == "<":
                self.in_tag = True
            elif c == ">":
                self.in_tag = False
            elif not self.in_tag:
                self._process_character_outside_tag(c)
        self.body = ""
        return "".join(self.rendered)

    def _process_character_outside_tag(self, c):
        if c == "&":
            self.in_entity = True
        if self.in_entity:
            self.entity += c
            if c == ";":
                self.rendered.append(parse_entity(self.entity))
                self.entity = ""
                self.in_entity = False
        else:
            self.rendered.append(c)


def parse_entity(entity):
    if entity == "&lt;":
        return "<"
    elif entity == "&gt;":
        return ">"
    return entity


def main():
    import sys

    if len(sys.argv) <= 1:
        sys.argv.append(DEFAULT_PAGE)
    for requested_url_string in sys.argv[1:]:
        print(URL(requested_url_string).load())


if __name__ == "__main__":
    main()
