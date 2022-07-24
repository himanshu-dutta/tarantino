from tarantino.http import HTTPRequest
from tarantino.http import HTTPResponse
from tarantino.imports import t
from tarantino.http.headers import Headers
from tarantino.http.utils import HTTPMethods, HTTPStatusCode


def detect_method_overridden(cls, obj):
    # https://stackoverflow.com/a/17008418
    common = cls.__dict__.keys() & obj.__class__.__dict__.keys()
    diff = [
        m
        for m in common
        if cls.__dict__[m] != obj.__class__.__dict__[m] and not m.startswith("_")
    ]
    return diff


class HTTPHandler:
    def __init__(self):
        ...

    async def get(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`get` method not implemented.")

    async def head(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`head` method not implemented.")

    async def post(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`post` method not implemented.")

    async def put(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`put` method not implemented.")

    async def delete(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`delete` method not implemented.")

    async def trace(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`trace` method not implemented.")

    async def patch(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        raise NotImplementedError("`patch` method not implemented.")

    @property
    def allowed_methods(self):
        am = ["options"]
        am += detect_method_overridden(HTTPHandler, self)
        am = [method.upper() for method in am]
        am = set(am)
        return am

    async def options(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        allowed_methods = self.allowed_methods
        headers = Headers()
        headers.set("allow", ", ".join(allowed_methods))
        return HTTPResponse("", HTTPStatusCode.STATUS_204_NO_CONTENT, headers)

    async def __call__(
        self,
        request: HTTPRequest,
        **kwargs,
    ) -> t.Awaitable[HTTPResponse]:
        method = str(request.method).lower()
        handler = getattr(self, method)
        return await handler(request, **kwargs)
