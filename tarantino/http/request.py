from tarantino.http.cookie import parse_cookies
from tarantino.http.headers import Headers
from tarantino.imports import json, parse


class Request:
    headers_encoding = "latin-1"
    body_encoding = "utf-8"

    def __init__(self, scope: dict, receive, send):
        self.scope = scope
        self.asgi_receive = receive
        self.asgi_send = send

        self.query_params = parse.parse_qs(self.scope.get("query_string", b"").decode())
        self.headers = Headers(headers_list=scope["headers"])
        self.cookies = parse_cookies(self.headers.get("cookie", "", decode=True))
        self.client = self.scope["client"]
        self.http_version = self.scope["http_version"]
        self.method = self.scope.get("method")
        self.path = self.scope.get("path")
        self.content_length = self.headers.get("content-length", decode=True)
        self.content_type = self.headers.get("content-type", decode=True)

        self._stream_consumed = False

    async def stream(self):
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return

        if self._stream_consumed:
            raise RuntimeError("Stream already consumed.")

        self._stream_consumed = True
        while True:
            message = await self.asgi_receive()
            body = message.get("body", b"")
            if body:
                yield body
            if not message.get("more_body", False):
                break
        yield b""

    async def body(self, as_str=False):
        if not hasattr(self, "_body"):
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)

        if as_str:
            return self._body.decode(self.body_encoding)
        return self._body

    async def text(self):
        return await self.body(as_str=True)

    async def bytes(self):
        return await self.body(as_str=False)

    async def json(self):
        if not hasattr(self, "_json"):
            self._json = json.loads(await self.body())
        return self._json
