from tarantino.imports import datetime, t


class Cookie:
    SAME_SITE_TYPES = ["Lax", "Strict", "None"]

    def __init__(
        self,
        key,
        value,
        *,
        domain: str = None,
        path: str = "/",
        expires: datetime = None,
        max_age: int = None,
        http_only: bool = False,
        secure: bool = False,
        same_site: t.Literal["Lax", "Strict", "None"] = "Lax",
    ):

        if expires and max_age:
            raise RuntimeError("Only one of expires and max_age must be non-None")

        if same_site not in type(self).SAME_SITE_TYPES:
            raise RuntimeError(f"same_site must be one of {type(self).SAME_SITE_TYPES}")

        self.key = key
        self.value = value

        self.domain = domain
        self.path = path
        self.expires = (
            expires.strftime("%a, %d %b %Y %H:%M:%S GMT") if expires else None
        )
        self.max_age = max_age
        self.http_only = http_only
        self.secure = secure
        self.same_site = same_site

    def __str__(self):
        cookie_str = f"{self.key}={self.value}"

        if self.domain:
            cookie_str += f"; Domain={self.domain}"

        if self.path:
            cookie_str += f"; Path={self.path}"

        if self.expires:
            cookie_str += f"; Expires={self.expires}"

        if self.max_age:
            cookie_str += f"; Max-Age={self.max_age}"

        if self.http_only:
            cookie_str += "; HttpOnly"

        if self.secure:
            cookie_str += "; Secure"

        if self.same_site:
            cookie_str += f"; SameSite={self.same_site}"

        return cookie_str

    def to_header(self):
        return (b"set-cookie", str(self).encode("utf-8"))
