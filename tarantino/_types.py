from .http import HTTPRequest, HTTPResponse
from .imports import re, t
from .websocket import WSConnection

Scope = t.MutableMapping[str, t.Any]
Message = t.MutableMapping[str, t.Any]

Receive = t.Callable[[], t.Awaitable[Message]]
Send = t.Callable[[Message], t.Awaitable[None]]
ASGIApp = t.Callable[[Scope, Receive, Send], t.Awaitable[None]]
HTTPCallback = t.Callable[[HTTPRequest, str], t.Awaitable[HTTPResponse]]
WSCallback = t.Callable[[WSConnection, str], t.Awaitable[None | HTTPResponse]]


class Middleware(t.Protocol):
    app: ASGIApp = ...

    def __init__(self, **options: t.Any):
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        ...


class CastType(t.Protocol):
    pattern: str | re.Pattern = ""

    def parse(self, segment: str) -> t.Any:
        ...
