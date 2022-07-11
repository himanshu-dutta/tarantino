from tarantino.http import Headers, HTTPRequest, HTTPResponse, HTTPStatusCode
from tarantino.imports import datetime, hashlib, t, wraps
from tarantino.types import HTTPCallback

_token_registry: t.Dict[str, "Credentials"] = dict()
COOKIE_NAME = "_sessionid"


class Credentials:
    def __init__(self, **kwargs):

        self._fields = list(kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

        if len(kwargs):
            self.authenticated_at = None

    def __str__(self):
        r = "Credentials("

        for idx, field in enumerate(self._fields):
            if idx > 0:
                r += ","

            r += f" {field}={getattr(self, field)}"

        r += " )"
        return r

    def dump(self) -> str:
        if len(self._fields):
            return "".join(
                list(map(lambda field: str(getattr(self, field)), self._fields))
            ) + datetime.now().strftime("%Y%m%d%H%M%S")
        else:
            return ""


class AuthenticationResponse(HTTPResponse):
    def __init__(
        self,
        request: HTTPRequest,
        creds: Credentials,
        redirect: str = "",
        max_age: int = 86400,
    ):

        token = request.cookies.get(COOKIE_NAME, "")
        old_cred = _token_registry.get(token, None)
        if old_cred:
            del _token_registry[token]

        auth_token = hashlib.sha256(creds.dump().encode("utf-8")).hexdigest()
        _token_registry[auth_token] = creds

        headers = Headers()
        status_code = HTTPStatusCode.STATUS_200_OK

        body = ""
        if redirect:
            headers.set("location", redirect.encode("utf-8"))
            status_code = HTTPStatusCode.STATUS_307_TEMPORARY_REDIRECT

        super().__init__(body=body, status=status_code, headers=headers)

        self.add_cookie(
            key=COOKIE_NAME,
            value=auth_token,
            http_only=True,
            max_age=max_age,
            same_site="Lax",
        )


_AnonymousCredentials = Credentials()


def authenticate(cb: HTTPCallback) -> HTTPCallback:
    @wraps(cb)
    def _inner(request: HTTPRequest, **kwargs):
        token = request.cookies.get(COOKIE_NAME, "")
        creds = _token_registry.get(token, _AnonymousCredentials)

        setattr(request, "credentials", creds)
        response = cb(request, **kwargs)

        return response

    _inner.__name__ = cb.__name__
    _inner.__qualname__ = cb.__qualname__
    _inner.__doc__ = cb.__doc__

    return _inner
