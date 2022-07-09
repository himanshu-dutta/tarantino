from .._types import MiddlewareType, ASGIApp, Message, Send
from ..http import HTTPStatusCode

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


class ErrorResponse(MiddlewareType):
    def __init__(self):
        self.app: ASGIApp = None
        self.has_sent_body = False

    async def __call__(self, scope, receive, send):
        send = self.error_send(send)
        return await self.app(scope, receive, send)

    def error_send(self, send: Send) -> Send:
        async def _wrapper(message: Message):
            if self.has_sent_body:
                return

            if message["type"] == "http.response.start" and message["status"] >= 400:
                status_code = message["status"]

                response = response_template % (
                    status_code,
                    status_code,
                    HTTPStatusCode.get_status_message(status_code),
                )
                response = response.encode()

                await send(message)

                await send(
                    {
                        "type": "http.response.body",
                        "body": response,
                        "more_body": False,
                    }
                )

                self.has_sent_body = True
                return

            await send(message)

        return _wrapper
