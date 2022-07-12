from tarantino.imports import t
from tarantino.websocket.connection import Connection
from tarantino.websocket.utils import WSStatusCode


class WebsocketHandler:
    def __init__(self):
        self.connection: Connection = None
        self.params: t.Dict[str, t.Any] = None

    async def on_connect(self):
        raise NotImplementedError("`on_connect` method not implemented.")

    async def on_message(self, text_data: str = None, bytes_data: bytes = None):
        raise NotImplementedError("`on_message` method not implemented.")

    async def on_disconnect(self, code: int):
        raise NotImplementedError("`on_disconnect` method not implemented.")

    async def send(self, *, text_data: str = None, bytes_data: bytes = None):
        await self.connection.send(text_data=text_data, bytes_data=bytes_data)

    async def accept(self, subprotocols: str = None):
        await self.connection.accept(subprotocols=subprotocols)

    async def close(
        self,
        code: int = WSStatusCode.STATUS_1000_NORMAL_CLOSURE,
        reason: str = "",
    ):
        await self.connection.close(code=code, reason=reason)

    async def setup(self, connection: Connection, **kwargs):
        self.connection = connection
        self.params = kwargs

    async def __call__(self, connection: Connection, **kwargs):
        await self.setup(connection, **kwargs)
        await self.on_connect()

        while True:
            event = await self.connection.receive()
            event_type = event["type"]

            if event_type == "websocket.receive":
                await self.on_message(
                    text_data=event.get("text"), bytes_data=event.get("bytes")
                )

            elif event_type == "websocket.disconnect":
                await self.on_disconnect(code=event["code"])
                break
