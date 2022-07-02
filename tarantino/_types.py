from .http import HTTPRequest, HTTPResponse
from .imports import t


class Callback(t.Protocol):
    def __call__(self, request: HTTPRequest, *args: str) -> HTTPResponse:
        ...
