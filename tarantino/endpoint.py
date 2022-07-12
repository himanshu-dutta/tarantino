from tarantino.http import (
    Headers,
    HTTPMethods,
    HTTPRequest,
    HTTPResponse,
    HTTPStatusCode,
)
from tarantino.imports import t
from tarantino.types import HTTPCallback, WSCallback
from tarantino.websocket import WSConnection


class Endpoint:
    """`Endpoint` consists of mapping between the `HTTP` methods and their
    respective handlers.

    It also maps `websocket` request to a handler.
    """

    method_names = dir(HTTPMethods) + ["websocket"]

    def __init__(self, path: str):
        self.path = path
        self.handlers: t.Dict[str, HTTPCallback | WSCallback] = dict()

    def __setattr__(self, name, value):
        if name in self.method_names:
            self.handlers[name] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.method_names:
            return self.handlers.get(name)
        else:
            raise AttributeError(
                f"Invalid method name: {name}. Allowed methods are:"
                f" {self.method_names}"
            )

    async def not_allowed_handler(self, status_code: int):
        http_method_not_allowed_response = HTTPResponse("", status_code, [])
        return http_method_not_allowed_response

    async def default_options_handler(self):
        headers = Headers()
        allowed_methods = ["OPTIONS"]

        for method in dir(HTTPMethods):
            if getattr(self, method) is not None:
                allowed_methods.append(method.upper())

        headers.set("allow", ", ".join(allowed_methods))

        return HTTPResponse("", HTTPStatusCode.STATUS_204_NO_CONTENT, headers)

    async def default_handler(
        self, conn_request: HTTPRequest | WSConnection, **kwargs
    ) -> t.Awaitable[HTTPResponse]:
        scope_type = conn_request.scope["type"]
        method_name = conn_request.scope.get("method", "").lower()

        if scope_type == "http":
            if method_name == "options":
                return await self.default_options_handler()
            return await self.not_allowed_handler(
                HTTPStatusCode.STATUS_405_METHOD_NOT_ALLOWED
            )

        elif scope_type == "websocket":
            return await self.not_allowed_handler(HTTPStatusCode.STATUS_403_FORBIDDEN)

        else:
            raise ValueError(f"Invalid scope type: {scope_type}")

    async def __call__(self, conn_request: HTTPRequest | WSConnection, **kwargs):
        method = str(getattr(conn_request, "method", "websocket")).lower()
        handler = getattr(self, method)
        if not handler:
            handler = self.default_handler

        return await handler(conn_request, **kwargs)
