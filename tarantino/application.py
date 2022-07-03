from .http import HTTPRequest, HTTPResponse
from .imports import t
from .router import Router
from .websocket import WSConnection
from ._types import MiddlewareType

_protocols = ["http", "websocket"]
PROTOCOLS_TYPE = t.Literal["http", "websocket"]


class Tarantino:
    def __init__(self, name, middlewares: t.Sequence[MiddlewareType] = None):
        self.name = name
        self.http_router = Router()
        self.ws_router = Router()

        self.app = self.build_middleware_stack(middlewares)

    def build_middleware_stack(self, middlewares: t.Sequence[MiddlewareType] = None):
        app = self.app

        if middlewares:
            for middleware in reversed(middlewares):
                middleware.app = app
                app = middleware

        return app

    def register_route(self, uri, protocol: PROTOCOLS_TYPE = "http"):
        def _outer(fn):
            if protocol not in _protocols:
                raise ValueError(f"Invalid protocol type: {protocol}")

            if protocol == "http":
                self.http_router.add(uri, fn)
            elif protocol == "websocket":
                self.ws_router.add(uri, fn)

            return fn

        return _outer

    async def app(self, scope, receive, send):

        scope_type = scope["type"]

        if scope_type == "http":

            events = list()
            while True:
                event = await receive()
                if event["type"] != "http.request":
                    raise RuntimeError(
                        'Expected to receive more ASGI "http.request" event.'
                    )
                events.append(event)
                if not event["more_body"]:
                    break
            request = HTTPRequest(scope, events)

            cb, args = self.http_router.find(request.uri)
            if cb is None:
                err = 'No callback found for the path: "%s"'
                raise NotImplementedError(err % request.uri)

            response = await cb(request, *args)
            assert issubclass(
                type(response), HTTPResponse
            ), f"Expected a response type: {HTTPResponse.__qualname__}"

            await send(
                {
                    "type": "http.response.start",
                    "status": response.get_status(),
                    "headers": response.get_headers(),
                }
            )

            await send(
                {
                    "type": "http.response.body",
                    "body": response.get_body(),
                    "more_body": False,
                }
            )

        elif scope_type == "websocket":
            uri = scope["path"]
            conn = WSConnection(scope, receive, send)
            cb, args = self.ws_router.find(uri)

            if cb is None:
                err = 'No callback found for the path: "%s"'
                raise NotImplementedError(err % uri)

            await cb(conn, *args)

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)

    def register_subapp(self, subapp: "SubApp"):
        self.http_router.merge(subapp.prefix, subapp.http_router)
        self.ws_router.merge(subapp.prefix, subapp.ws_router)


class SubApp:
    def __init__(self, prefix):
        self.prefix = prefix
        self.http_router = Router()
        self.ws_router = Router()

    def register_route(self, uri, protocol: PROTOCOLS_TYPE = "http"):
        def _outer(fn):
            if protocol not in _protocols:
                raise ValueError(f"Invalid protocol type: {protocol}")

            if protocol == "http":
                self.http_router.add(uri, fn)
            elif protocol == "websocket":
                self.ws_router.add(uri, fn)

            return fn

        return _outer

    def register_subapp(self, subapp: "SubApp"):
        self.http_router.merge(subapp.prefix, subapp.http_router)
        self.ws_router.merge(subapp.prefix, subapp.ws_router)
