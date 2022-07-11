from tarantino.http.cookie import Cookie
from tarantino.http.headers import Headers
from tarantino.http.utils import HTTPStatusCode
from tarantino.imports import datetime, json, t


class Response:
    def __init__(
        self,
        body: str | bytes,
        status: int,
        headers: Headers | t.Dict[str, str] = None,
    ):
        self.body = body
        self.status = status
        self.headers = (
            headers if isinstance(headers, Headers) else Headers(headers=headers)
        )

        self.cookies: t.List[Cookie] = list()

        assert self.assert_status_code(), f"Invalid status code: {self.status}"

    def assert_status_code(self):
        http_dir = dir(HTTPStatusCode)
        for attr_name in http_dir:
            if attr_name.startswith("STATUS_"):
                if getattr(HTTPStatusCode, attr_name) == self.status:
                    return True
        return False

    def add_cookie(
        self,
        key: str,
        value: str,
        *,
        domain: str = None,
        path: str = "/",
        expires: datetime = None,
        max_age: int = None,
        http_only: bool = False,
        secure: bool = False,
        same_site: t.Literal["Lax", "Strict", "None"] = "None",
    ):
        cookie = Cookie(
            key=key,
            value=value,
            domain=domain,
            path=path,
            expires=expires,
            max_age=max_age,
            http_only=http_only,
            secure=secure,
            same_site=same_site,
        )
        self.cookies.append(cookie.to_header())

    def get_status(self):
        return self.status

    def get_headers(self):
        return self.headers.getlist() + self.cookies

    def get_body(self):
        if isinstance(self.body, str):
            body = self.body.encode("utf-8")
        return body


class HTMLResponse(Response):
    def __init__(self, body: str | bytes, status: int):
        headers = [(b"content-type", b"text/html; charset=utf8")]
        super().__init__(body, status, headers)


class HTTP200Response(Response):
    def __init__(self, body: str | bytes):
        headers = [(b"content-type", b"text/html; charset=utf8")]
        super().__init__(body, HTTPStatusCode.STATUS_200_OK, headers)


class HTTP404Response(Response):
    def __init__(self):
        headers = [(b"content-length", 0)]
        super().__init__("", HTTPStatusCode.STATUS_404_NOT_FOUND, headers)


class JSONResponse(Response):
    def __init__(
        self,
        body: t.Any,
        status: int = HTTPStatusCode.STATUS_200_OK,
    ):
        body = json.dumps(body)
        headers = [(b"content-type", b"application/json")]
        super().__init__(body, status, headers)
