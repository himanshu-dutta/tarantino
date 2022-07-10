from tarantino.http.utils import HTTPStatusCode
from .._types import Middleware, Message, Send
from ..imports import t, re

from ..http import Headers


class Cors(Middleware):
    def __init__(
        self,
        allow_origins: t.Sequence[str] = (),
        allow_headers: t.Sequence[str] = (),
        allow_credentials: bool = False,
        allow_origin_regex: t.Optional[str] = None,
        expose_headers: t.Sequence[str] = (),
        max_age: int = 86400,
    ):
        self.app = None

        self.allow_origins = allow_origins
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers
        self.max_age = max_age

        self.allow_origin_regex = None
        if allow_origin_regex:
            self.allow_origin_regex = re.compile(allow_origin_regex)

        self.wildcard_resposne = not allow_credentials
        self.allow_all_origins = "*" in self.allow_origins
        self.allow_all_headers = "*" in self.allow_headers

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        request_headers = Headers(scope=scope)
        origin = request_headers.get("origin", "", decode=True)

        if origin:
            if method == "OPTIONS" and request_headers.get(
                "access-control-request-method",
                None,
            ):
                send = self.preflight_send(send, request_headers)
            else:
                send = self.simple_send(send, request_headers)

        await self.app(scope, receive, send)

    def access_control_allow_origin(
        self,
        origin: str,
        headers: Headers,
        explicit: bool = False,
    ):
        if self.allow_all_origins:
            if self.wildcard_resposne and not explicit:
                headers.set("access-control-allow-origin", "*")
            else:
                headers.set("access-control-allow-origin", origin)
                headers.set("vary", "origin")
            return False

        if self.allow_origin_regex and self.allow_origin_regex.fullmatch(origin):
            headers.set("access-control-allow-origin", origin)
            headers.set("vary", "origin")
            return False

        if origin in self.allow_origins:
            headers.set("access-control-allow-origin", origin)
            headers.set("vary", "origin")
            return False

        return True

    def access_control_allow_methods(self, headers: Headers, ac_request_method: str):
        allowed_methods = [
            header.strip()
            for header in headers.get("allow", "", decode=True).split(",")
        ]
        headers.pop("allow")
        headers.setdefault("access-control-allow-methods", ", ".join(allowed_methods))

        if ac_request_method not in allowed_methods:
            return True
        return False

    def access_control_allow_credentials(self, headers: Headers):
        if self.allow_credentials:
            headers.set("access-control-allow-credentials", "true")

    def access_control_max_age(self, headers: Headers):
        headers.set("access-control-max-age", self.max_age)

    def access_control_allow_headers(self, headers: Headers, request_headers: str):
        if request_headers:
            if self.allow_all_headers:
                headers.set("access-control-allow-headers", request_headers)
            else:
                headers.set(
                    "access-control-allow-headers",
                    ", ".join(self.allow_headers),
                )

                for header in [h.strip().lower() for h in request_headers.split(",")]:
                    if header not in self.allow_headers:
                        return True
        return False

    def access_control_expose_headers(self, headers: Headers):
        if self.expose_headers:
            headers.set("access-control-expose-headers", ", ".join(self.expose_headers))

    def preflight_send(self, send: Send, request_headers: Headers):
        async def _wrapper(message: Message):
            message_type = message["type"]

            if message_type == "http.response.start":
                status_code = message["status"]
                response_headers = Headers(headers=message["headers"])

                origin = request_headers.get("origin")
                ac_request_method = request_headers.get(
                    "access-control-request-method",
                    decode=True,
                )
                ac_request_headers = request_headers.get(
                    "access-control-request-headers",
                    default="",
                    decode=True,
                )

                err = False
                err = err or self.access_control_allow_origin(origin, response_headers)
                err = err or self.access_control_allow_methods(
                    response_headers, ac_request_method
                )
                err = err or self.access_control_allow_headers(
                    response_headers, ac_request_headers
                )
                self.access_control_allow_credentials(response_headers)
                self.access_control_max_age(response_headers)
                self.access_control_expose_headers(response_headers)

                if err:
                    status_code = HTTPStatusCode.STATUS_400_BAD_REQUEST

                print("Response Headers: ", response_headers._headers)

                message = {
                    "type": "http.response.start",
                    "status": status_code,
                    "headers": response_headers.getlist(),
                }

            await send(message)

        return _wrapper

    def simple_send(self, send: Send, request_headers: Headers):
        async def _wrapper(message: Message):
            message_type = message["type"]

            if message_type == "http.response.start":
                status_code = message["status"]
                response_headers = Headers(headers=message["headers"])

                origin = request_headers.get("origin")
                has_cookie = True if request_headers.get("cookie", None) else False

                self.access_control_allow_origin(
                    origin,
                    response_headers,
                    explicit=has_cookie,
                )
                self.access_control_allow_credentials(response_headers)
                self.access_control_expose_headers(response_headers)

                message = {
                    "type": "http.response.start",
                    "status": status_code,
                    "headers": response_headers.getlist(),
                }

            await send(message)

        return _wrapper
