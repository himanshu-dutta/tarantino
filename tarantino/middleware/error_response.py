from .._types import ASGIApp, Message, Middleware, Send
from ..http import Headers, HTTPStatusCode

response_template = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Error %s</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                height: 100vh;
                width: 100vw;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: Arial, Helvetica, sans-serif;
                background-color: #eeeeee;
            }

            .error-container {
                height: 4em;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .status-code {
                font-size: 3rem;
                padding: 1rem 1rem;
                color: #636e72;
            }
            .status-message {
                padding: 1rem 1rem;
                font-size: 2rem;
                color: #2d3436;
            }
            .divider {
                height: 4rem;
                border: 1px solid #bbbbbb;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="status-code">%s</div>
            <div class="divider"></div>
            <div class="status-message">%s</div>
        </div>
    </body>
</html>
"""


class ErrorResponse(Middleware):
    def __init__(self):
        self.app: ASGIApp = None

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        send = self.error_send(send)
        await self.app(scope, receive, send)

    def error_send(self, send: Send, has_sent_body: bool = False) -> Send:
        async def _wrapper(message: Message):
            nonlocal has_sent_body
            if has_sent_body:
                return

            if message["type"] == "http.response.start" and message["status"] >= 400:
                status_code = message["status"]
                headers = Headers(headers=message["headers"])

                response = response_template % (
                    status_code,
                    status_code,
                    HTTPStatusCode.get_status_message(status_code),
                )
                response = response.encode("utf-8")

                headers.set("content-length", len(response))
                headers.set("content-type", "text/html; charset=utf8")

                message = {
                    "type": "http.response.start",
                    "status": status_code,
                    "headers": headers.getlist(),
                }

                await send(message)

                await send(
                    {
                        "type": "http.response.body",
                        "body": response,
                        "more_body": False,
                    }
                )

                has_sent_body = True
                return

            await send(message)

        return _wrapper
