from tarantino.http.headers import Headers
from tarantino.imports import json, parse, t


class Request:
    def __init__(self, scope: dict, events: t.List[dict] = None):
        self.scope = scope

        self.query_params = parse.parse_qs(self.scope.get("query_string", b"").decode())
        self.headers = Headers(headers_list=scope["headers"])
        self.cookies = self.parse_cookies(self.headers.get("cookie", "", decode=True))

        self.client = self.scope["client"]
        self.http_version = self.scope["http_version"]
        self.method = self.scope.get("method")
        self.path = self.scope.get("path")
        self.content_length = self.headers.get("content-length", decode=True)
        self.content_type = self.headers.get("content-type", decode=True)

        self._body = self.parse_body(events) if events else bytes()

    async def body(self, as_str=False):
        if as_str:
            self._body.decode("utf-8")
        return self._body

    async def text(self):
        return await self.body(as_str=True)

    async def bytes(self):
        return await self.body(as_str=False)

    async def json(self):
        return json.loads(await self.body())

    @staticmethod
    def parse_cookies(cookie_str: str) -> t.Dict[str, str]:
        if isinstance(cookie_str, bytes):
            cookie_str = cookie_str.decode("latin-1")
        cookie_strs = cookie_str.split("; ")

        cookies = dict()

        def _(cs: str):
            delim = cs.find("=")
            k = cs[:delim]
            v = cs[delim + 1 :]

            cookies[k] = v

        list(map(_, cookie_strs))
        return cookies

    @staticmethod
    def parse_body(events: t.List[dict]):
        chunk = [event["body"] for event in events]
        body = b"".join(chunk)
        return body
