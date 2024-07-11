import socket


class URL:

    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"
        if "/" not in url:
            url += "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        with socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
        ) as s:
            s.connect((self.host, 80))
            request = self._build_request()
            s.send(request.encode("utf8"))
            response = s.makefile("r", encoding="utf8", newline="\r\n")
            content = self._parse_response(response)
        return content

    def _build_request(self):
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
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
            if line == "\r\n": break
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
        return ''.join(rendered)

    def load(self):
        body = self.request()
        return self.show(body)


def main():
    print(URL("http://example.org").load())


if __name__ == '__main__':
    main()
