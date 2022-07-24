from tarantino.casts import CastRegistry
from tarantino.endpoint import HTTPEndpoint, WebsocketEndpoint
from tarantino.http import HTTPMethods
from tarantino.imports import t
from tarantino.router import Router
from tarantino.types import CastType, Middleware


class Tarantino:
    def __init__(self, name, *, middlewares: t.Sequence[Middleware] = None):
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
        CastRegistry.register_cast(cast_name, cast)

    def register_http_endpoint(self, path: str, methods: t.List[str], *args, **kwargs):
        def _wrapper(fn):
            for method in methods:
                if method.upper() not in dir(HTTPMethods):
                    raise ValueError(f"Invalid method: {method}")

            endpoint: HTTPEndpoint = self.router.setdefault_endpoint(
                path,
                HTTPEndpoint(path),
            )

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            endpoint.add_handler(handler, methods)
            return fn

        return _wrapper

    def register_websocket_endpoint(self, path: str, *args, **kwargs):
        def _wrapper(fn):
            endpoint: WebsocketEndpoint = self.router.setdefault_endpoint(
                path,
                WebsocketEndpoint(path),
            )

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            endpoint.add_handler(handler)

        return _wrapper

    async def app(self, scope, receive, send):
        scope_type = scope["type"]
        if scope_type not in ["http", "websocket"]:
            raise RuntimeError(f"Invalid scope type: {scope_type}")

        path: str = scope["path"]
        endpoint, kwargs = self.router.match_uri(path)
        if endpoint is None:
            err = 'No callback found for the path: "%s"'
            raise NotImplementedError(err % path)
        await endpoint(scope, receive, send, **kwargs)

    async def __call__(self, scope, receive, send):
        scope["app"] = self
        return await self.asgi_app(scope, receive, send)

    def get(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["get"], *args, **kwargs)

    def head(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["head"], *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["post"], *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["put"], *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["delete"], *args, **kwargs)

    def options(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["options"], *args, **kwargs)

    def trace(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["trace"], *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["patch"], *args, **kwargs)

    def websocket(self, path: str, *args, **kwargs):
        return self.register_websocket_endpoint(path, *args, **kwargs)

    def http(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(
            path, methods=dir(HTTPMethods), *args, **kwargs
        )

    def register_subapp(self, subapp: "SubApp"):
        self.router.merge_router(subapp.prefix, subapp.router)


class SubApp:
    def __init__(self, prefix):
        self.prefix = prefix
        self.router = Router()

    def register_cast(self, cast_name: str, cast: CastType):
        CastRegistry.register_cast(cast_name, cast)

    def register_http_endpoint(self, path: str, methods: t.List[str], *args, **kwargs):
        def _wrapper(fn):
            for method in methods:
                if method.upper() not in dir(HTTPMethods):
                    raise ValueError(f"Invalid method: {method}")

            endpoint: HTTPEndpoint = self.router.setdefault_endpoint(
                path,
                HTTPEndpoint(path),
            )

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            endpoint.add_handler(handler, methods)
            return fn

        return _wrapper

    def register_websocket_endpoint(self, path: str, *args, **kwargs):
        def _wrapper(fn):
            endpoint: WebsocketEndpoint = self.router.setdefault_endpoint(
                path,
                WebsocketEndpoint(path),
            )

            handler = fn(*args, **kwargs) if isinstance(fn, type) else fn
            endpoint.add_handler(handler)

        return _wrapper

    def get(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["get"], *args, **kwargs)

    def head(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["head"], *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["post"], *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["put"], *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["delete"], *args, **kwargs)

    def options(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["options"], *args, **kwargs)

    def trace(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["trace"], *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(path, methods=["patch"], *args, **kwargs)

    def websocket(self, path: str, *args, **kwargs):
        return self.register_websocket_endpoint(path, *args, **kwargs)

    def http(self, path: str, *args, **kwargs):
        return self.register_http_endpoint(
            path, methods=dir(HTTPMethods), *args, **kwargs
        )

    def register_subapp(self, subapp: "SubApp"):
        self.router.merge_router(subapp.prefix, subapp.router)
