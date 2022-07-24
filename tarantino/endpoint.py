from tarantino.http import (
    Headers,
    HTTPMethods,
    HTTPRequest,
    HTTPResponse,
    HTTPStatusCode,
)
from tarantino.imports import t
from tarantino.types import HTTPHandler, WebsocketHandler
from tarantino.websocket import WebsocketConnection


class Endpoint:
    async def __call__(self, scope, receive, send, **kwargs):
        raise NotImplementedError()


class HTTPEndpoint(Endpoint):
    def __init__(self, path):
        self.path = path
        self.method_handlers: t.Dict[str, HTTPHandler] = dict()

    async def __call__(self, scope, receive, send, **kwargs):
        response: HTTPResponse = None
        method = scope["method"]
        if method not in self.method_handlers:
            if method == "OPTIONS":
                response = await self.default_options_handler()
            response = await self.method_not_allowed_handler()
        else:
            handler = self.method_handlers[method]
            request = HTTPRequest(scope, receive, send)
            response: HTTPResponse = await handler(request, **kwargs)
        await response(scope, receive, send)

    async def method_not_allowed_handler(self):
        return HTTPResponse("", HTTPStatusCode.STATUS_405_METHOD_NOT_ALLOWED)

    async def default_options_handler(self):
        allowed_methods = set(["OPTIONS"] + list(self.method_handlers.keys()))
        headers = Headers()
        headers.set("allow", ", ".join(allowed_methods))
        return HTTPResponse("", HTTPStatusCode.STATUS_204_NO_CONTENT, headers)

    def add_handler(self, handler: HTTPHandler, methods: t.List[str]):
        for method in methods:
            if method.upper() not in dir(HTTPMethods):
                raise ValueError(f"Invalid method: {method}")
            if method.upper() in self.method_handlers:
                raise ValueError(f"Handler already exists for method: {method}")

            self.method_handlers[method.upper()] = handler

    def extend(self, o: "HTTPEndpoint"):
        method_handlers = o.method_handlers
        overlapping_methods = set(self.method_handlers.keys()).intersection(
            set(method_handlers.keys())
        )

        if overlapping_methods:
            overlapping_methods = ", ".join(overlapping_methods)
            raise ValueError(f"Found overlapping methods: {overlapping_methods}")

        self.method_handlers.update(method_handlers)


class WebsocketEndpoint(Endpoint):
    def __init__(self, path):
        self.path = path
        self.handler: WebsocketHandler = None

    async def __call__(self, scope, receive, send, **kwargs):
        assert self.handler is not None, "No handler for the path"

        connection = WebsocketConnection(scope, receive, send)
        await self.handler(connection, **kwargs)

    def add_handler(self, handler: WebsocketHandler):
        if self.handler:
            raise ValueError(f"Handler already exists")
        self.handler = handler
