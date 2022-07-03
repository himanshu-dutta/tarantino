from .http import HTTPRequest, HTTPResponse
from .imports import t

Scope = t.MutableMapping[str, t.Any]
Message = t.MutableMapping[str, t.Any]

Receive = t.Callable[[], t.Awaitable[Message]]
Send = t.Callable[[Message], t.Awaitable[None]]
ASGIApp = t.Callable[[Scope, Receive, Send], t.Awaitable[None]]


class HTTPCallback(t.Protocol):
    def __call__(self, request: HTTPRequest, *args: str) -> HTTPResponse:
        ...


class MiddlewareType(t.Protocol):
    def __init__(self, **options: t.Any):
        ...

    def __call__(self, scope: Scope, receive: Receive, send: Send):
        ...

    @property
    def app(self) -> ASGIApp:
        ...

    @app.setter
    def app(self, app: ASGIApp) -> None:
        ...
