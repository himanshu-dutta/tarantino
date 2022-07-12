from tarantino.http.headers import Headers


def test_scope_headers():
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "server": ("127.0.0.1", 8080),
        "client": ("127.0.0.1", 57392),
        "scheme": "http",
        "root_path": "",
        "headers": [
            (b"host", b"localhost:8080"),
            (b"connection", b"keep-alive"),
            (
                b"sec-ch-ua",
                b'".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            ),
            (
                b"sec-ch-ua-full-version-list",
                b'".Not/A)Brand";v="99.0.0.0", "Google Chrome";v="103.0.5060.53", "Chromium";v="103.0.5060.53"',
            ),
            (b"sec-ch-ua-mobile", b"?0"),
            (
                b"user-agent",
                b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            ),
            (b"sec-ch-ua-arch", b'"arm"'),
            (b"sec-ch-ua-full-version", b'"103.0.5060.53"'),
            (b"sec-ch-ua-platform-version", b'"12.4.0"'),
            (b"sec-ch-ua-bitness", b'"64"'),
            (b"sec-ch-ua-model", b""),
            (b"sec-ch-ua-platform", b'"macOS"'),
            (b"accept", b"*/*"),
            (b"origin", b"localhost:8000"),
            (b"sec-fetch-site", b"cross-site"),
            (b"sec-fetch-mode", b"cors"),
            (b"sec-fetch-dest", b"empty"),
            (b"referer", b"localhost:8000"),
            (b"accept-encoding", b"gzip, deflate, br"),
            (b"accept-language", b"en-US,en;q=0.9"),
        ],
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "app": "<tarantino.application.Tarantino object at 0x1044b3af0>",
    }

    headers = Headers(headers_list=scope["headers"])

    assert headers.get("host", decode=True) == "localhost:8080"
    assert headers.get("connection", decode=True) == "keep-alive"
    assert headers.get("origin", decode=True) == "localhost:8000"
    assert headers.get("accept-encoding", decode=True) == "gzip, deflate, br"
    assert headers.get("accept-language", decode=True) == "en-US,en;q=0.9"


def test_dict_headers():
    headers_dict = {
        "set-cookie": [
            "_auth=aeijijsfoiwo943adf; Domain=localhost:8080; path=/",
            "_csrftoken=5nksflnsfweirj23ij; Domain=localhost; path=/; HttpOnly; Secure; SameSite=Lax",
        ],
        "content-type": "text/html",
        "content-length": 1023,
    }

    headers = Headers(headers_dict=headers_dict)
    headers.set("allow", "GET, HEAD, OPTIONS")

    set_cookie = headers.get("set-cookie", decode=True)
    assert (
        isinstance(set_cookie, list)
        and len(set_cookie) == 2
        and set_cookie[0] == "_auth=aeijijsfoiwo943adf; Domain=localhost:8080; path=/"
        and set_cookie[1]
        == "_csrftoken=5nksflnsfweirj23ij; Domain=localhost; path=/; HttpOnly; Secure; SameSite=Lax"
    )
    assert headers.get("content-type", decode=True) == "text/html"
    assert headers.get("content-length", decode=True) == "1023"
    assert headers.get("allow", decode=True) == "GET, HEAD, OPTIONS"


def test_header_methods():
    headers = Headers()

    headers.set(
        "set-cookie",
        "_auth=aeijijsfoiwo943adf; Domain=localhost:8080; path=/",
        mode="append",
    )
    headers.set(
        "set-cookie",
        "_csrftoken=5nksflnsfweirj23ij; Domain=localhost; path=/; HttpOnly; Secure; SameSite=Lax",
        mode="append",
    )
    headers.set("content-type", "application/json")
    headers.set("content-length", 1023)

    assert headers.get("content-type", decode=True) == "application/json"
    assert headers.get("content-length", decode=True) == "1023"

    set_cookie = headers.get("set-cookie", decode=True)
    assert (
        isinstance(set_cookie, list)
        and len(set_cookie) == 2
        and set_cookie[0] == "_auth=aeijijsfoiwo943adf; Domain=localhost:8080; path=/"
        and set_cookie[1]
        == "_csrftoken=5nksflnsfweirj23ij; Domain=localhost; path=/; HttpOnly; Secure; SameSite=Lax"
    )

    del headers["content-type"]

    assert b"content-type" not in headers._headers

    ct = headers.setdefault("content-type", "text/html", decode=True)
    assert ct == "text/html"
    assert headers.get("content-type", decode=True) == "text/html"
