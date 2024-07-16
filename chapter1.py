import pathlib
import socket
import ssl
from enum import Enum, StrEnum, auto

DEFAULT_PAGE = "file://./example1-simple.html"


class Scheme(StrEnum):
    http = auto()
    https = auto()
    file = auto()
    data = auto()


class URL:
    def __init__(self, url):
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
        with socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        ) as s:
            s.connect((self.host, self.port))
            if self.scheme == Scheme.https:
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            request = self._build_request()
            s.send(request.encode("utf8"))
            response = s.makefile("r", encoding="utf8", newline="\r\n")
        return response

    def _build_request(self):
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Connection: close\r\n"
        request += "User-Agent: giraffe\r\n"
        request += "\r\n"
        return request

    def _parse_response(self, response):
        version, status, explanation = self._parse_statusline(response)
        headers = self._parse_headers(response)
        content = response.read()
        return content

    def _parse_statusline(self, response):
        statusline = response.readline()
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

    def show(self, body):
        in_tag = False
        rendered = []
        for c in body:
            if c == "<":
                in_tag = True
            elif c == ">":
                in_tag = False
            elif not in_tag:
                rendered.append(c)
        return "".join(rendered)

    def load(self):
        body = self.request()
        return self.show(body)


def main():
    import sys

    requested_url_string = DEFAULT_PAGE if len(sys.argv) <= 1 else sys.argv[1]
    print(URL(requested_url_string).load())


if __name__ == "__main__":
    main()
