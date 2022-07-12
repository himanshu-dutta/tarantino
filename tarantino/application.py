from tarantino.endpoint import Endpoint
from tarantino.http import HTTPMethods, HTTPRequest, HTTPResponse
from tarantino.imports import t
from tarantino.router import Router
from tarantino.types import CastType, Middleware
from tarantino.websocket import WSConnection


class Tarantino:
    method_names = dir(HTTPMethods) + ["websocket"]

    def __init__(self, name, middlewares: t.Sequence[Middleware] = None):
        self.name = name
        self.router = Router()

        self.asgi_app = self.build_middleware_stack(middlewares)

    def build_middleware_stack(self, middlewares: t.Sequence[Middleware] = None):
        app = self.app

        if middlewares:
            for middleware in reversed(middlewares):
                middleware.app = app
                app = middleware

        return app

    def register_cast(self, cast_name: str, cast: CastType):
        self.router.register_cast(cast_name, cast)

    def register_endpoint(self, path: str, methods: t.List[str], *args, **kwargs):
        def _wrapper(fn):
            for method in methods:
                if method not in self.method_names:
                    raise ValueError(f"Invalid method: {method}")

            endpoint = self.router.setdefault_endpoint(path, Endpoint(path))

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            for method in methods:
                setattr(endpoint, method, handler)

            return fn

        return _wrapper

    async def http_handler(self, scope, receive, send):
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
        endpoint, kwargs = self.router.match_uri(request.path)

        if endpoint is None:
            err = 'No callback found for the path: "%s"'
            raise NotImplementedError(err % request.path)

        response = await endpoint(request, **kwargs)

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

    async def ws_handler(self, scope, receive, send):

        conn = WSConnection(scope, receive, send)
        endpoint, kwargs = self.router.match_uri(conn.http_request.path)

        if endpoint is None:
            err = 'No callback found for the path: "%s"'
            raise NotImplementedError(err % conn.http_request.path)

        response = await endpoint(conn, **kwargs)

        if response:
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

    async def app(self, scope, receive, send):
        scope_type = scope["type"]

        if scope_type == "http":
            await self.http_handler(scope, receive, send)
        elif scope_type == "websocket":
            await self.ws_handler(scope, receive, send)
        else:
            raise ValueError(f"Invalid scope type: {scope_type}")

    async def __call__(self, scope, receive, send):
        scope["app"] = self
        return await self.asgi_app(scope, receive, send)

    def register_subapp(self, subapp: "SubApp"):
        self.router.merge_router(subapp.prefix, subapp.router)

    def get(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["get"], *args, **kwargs)

    def head(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["head"], *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["post"], *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["put"], *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["delete"], *args, **kwargs)

    def connect(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["connect"], *args, **kwargs)

    def options(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["options"], *args, **kwargs)

    def trace(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["trace"], *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["patch"], *args, **kwargs)

    def websocket(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["websocket"], *args, **kwargs)


class SubApp:
    method_names = dir(HTTPMethods) + ["websocket"]

    def __init__(self, prefix):
        self.prefix = prefix
        self.router = Router()

    def register_cast(self, cast_name: str, cast: CastType):
        self.router.register_cast(cast_name, cast)

    def register_endpoint(self, path: str, methods: t.List[str], *args, **kwargs):
        def _wrapper(fn):
            for method in methods:
                if method not in self.method_names:
                    raise ValueError(f"Invalid method: {method}")

            endpoint = self.router.setdefault_endpoint(path, Endpoint(path))

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            for method in methods:
                setattr(endpoint, method, handler)

            return fn

        return _wrapper

    def get(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["get"], *args, **kwargs)

    def head(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["head"], *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["post"], *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["put"], *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["delete"], *args, **kwargs)

    def connect(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["connect"], *args, **kwargs)

    def options(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["options"], *args, **kwargs)

    def trace(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["trace"], *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["patch"], *args, **kwargs)

    def websocket(self, path: str, *args, **kwargs):
        return self.register_endpoint(path, methods=["websocket"], *args, **kwargs)

    def register_subapp(self, subapp: "SubApp"):
        self.router.merge_router(subapp.prefix, subapp.router)
