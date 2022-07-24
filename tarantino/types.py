from tarantino.http import HTTPRequest, HTTPResponse
from tarantino.imports import t
from tarantino.websocket import WebsocketConnection

Scope = t.MutableMapping[str, t.Any]
Message = t.MutableMapping[str, t.Any]

Receive = t.Callable[[], t.Awaitable[Message]]
Send = t.Callable[[Message], t.Awaitable[None]]
ASGIApp = t.Callable[[Scope, Receive, Send], t.Awaitable[None]]
HTTPHandler = t.Callable[[HTTPRequest, str], t.Awaitable[HTTPResponse]]
WebsocketHandler = t.Callable[
    [WebsocketConnection, str], t.Awaitable[None | HTTPResponse]
]


class Middleware(t.Protocol):
    app: ASGIApp = ...

    def __init__(self, **options: t.Any):
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        ...


T = t.TypeVar("T")


class CastType(t.Generic[T]):
    pattern: str = ""

    @staticmethod
    def parse(value: str) -> T:
        ...

    @staticmethod
    def to_str(value: T) -> str:
        ...
