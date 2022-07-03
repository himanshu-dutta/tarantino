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
