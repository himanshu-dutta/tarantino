from tarantino.http.cookie import Cookie
from tarantino.http.headers import Headers
from tarantino.http.utils import HTTPStatusCode
from tarantino.imports import datetime, json, parse, t


class Response:
    headers_encoding = "latin-1"
    body_encoding = "utf-8"
    default_content_type = None

    def __init__(
        self,
        body: t.Any,
        status: int,
        headers: Headers | t.Dict[str, str] = None,
        content_type: str = None,
    ):
        self.body = body
        self.status = status
        self.headers = (
            headers if isinstance(headers, Headers) else Headers(headers=headers)
        )
        self.content_type = content_type if content_type else self.default_content_type
        self.cookies: t.List[Cookie] = list()

        assert self.assert_status_code(), f"Invalid status code: {self.status}"
        self.render()

    def assert_status_code(self):
        return self.status in [
            getattr(HTTPStatusCode, attr) for attr in dir(HTTPStatusCode)
        ]

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
        same_site: t.Literal["Lax", "Strict", "None"] = "Lax",
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

    def delete_cookie(
        self,
        key: str,
        *,
        domain: str = None,
        path: str = "/",
        http_only: bool = False,
        secure: bool = False,
        same_site: t.Literal["Lax", "Strict", "None"] = "Lax",
    ) -> None:
        self.add_cookie(
            key,
            "",
            domain=domain,
            path=path,
            expires=0,
            max_age=0,
            http_only=http_only,
            secure=secure,
            same_site=same_site,
        )

    def get_status(self):
        return self.status

    def get_headers(self):
        return self.headers.getlist() + self.cookies

    def get_body(self):
        return self.body

    def render(self):
        self.body = (
            self.body
            if isinstance(self.body, bytes)
            else str(self.body).encode(self.body_encoding)
        )
        if self.content_type:
            self.headers.set("content-type", self.content_type)
        self.headers.set("content-length", len(self.body))


class PlainTextResponse(Response):
    def __init__(
        self,
        body: t.Any,
        status: int,
        headers: Headers | t.Dict[str, str] = None,
    ):
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type="text/plain; charset=utf8",
        )


class HTMLResponse(Response):
    def __init__(
        self,
        body: t.Any,
        status: int,
        headers: Headers | t.Dict[str, str] = None,
    ):
        super().__init__(
            body=body,
            status=status,
            headers=headers,
            content_type="text/html; charset=utf8",
        )


class HTTP200Response(Response):
    def __init__(
        self,
        body: t.Any,
        headers: Headers | t.Dict[str, str] = None,
        content_type: str = None,
    ):
        super().__init__(
            body=body,
            status=HTTPStatusCode.STATUS_200_OK,
            headers=headers,
            content_type=content_type,
        )


class HTTP404Response(Response):
    def __init__(
        self,
        body: t.Any = "",
        headers: Headers | t.Dict[str, str] = None,
        content_type: str = None,
    ):
        super().__init__(
            body=body,
            status=HTTPStatusCode.STATUS_404_NOT_FOUND,
            headers=headers,
            content_type=content_type,
        )


class JSONResponse(Response):
    def __init__(
        self,
        body: t.Any,
        status: int,
        headers: Headers | t.Dict[str, str] = None,
    ):
        super().__init__(
            body=json.dumps(body),
            status=status,
            headers=headers,
            content_type="application/json",
        )


class RedirectResponse(Response):
    def __init__(
        self,
        url: str,
        status: int = HTTPStatusCode.STATUS_307_TEMPORARY_REDIRECT,
        headers: Headers | t.Dict[str, str] = None,
    ) -> None:
        super().__init__(
            body="",
            status=status,
            headers=headers,
        )
        self.headers.set(
            "location",
            parse.quote(str(url), safe=":/%#?=@[]!$&'()*+,;"),
        )
