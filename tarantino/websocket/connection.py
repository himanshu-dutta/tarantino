from ..http import HTTPRequest
from ..imports import enum, json, t
from .utils import WSStatusCode


class ConnecionState(enum.Enum):

    CONNECTING = enum.auto()
    OPENED = enum.auto()
    CLOSED = enum.auto()


# CONNECTING --> OPEN --> CLOSE

_MSG_MODES = ["text", "bytes"]


class Connection:
    def __init__(self, scope, receive, send):
        self.http_request = HTTPRequest(scope, None)

        self.scope = scope
        self.asgi_receive = receive
        self.asgi_send = send

        self.connection_state = ConnecionState.CONNECTING

    async def accept(self, subprotocols: str = None):
        if self.connection_state != ConnecionState.CONNECTING:
            msg = "Unexpected call to accept %s connection." % (self.connection_state)
            raise RuntimeError(msg)

        await self.receive()
        await self.asgi_send(
            {
                "type": "websocket.accept",
                "subprotocols": subprotocols,
            }
        )
        self.connection_state = ConnecionState.OPENED

    async def close(
        self, code: int = WSStatusCode.STATUS_1000_NORMAL_CLOSURE, reason: str = ""
    ):
        if self.connection_state == ConnecionState.CLOSED:
            msg = "Unepected call to close %s connection." % (self.connection_state)
            raise RuntimeError(msg)

        await self.asgi_send(
            {
                "type": "websocket.close",
                "code": code,
                "reason": reason,
            }
        )

        self.connection_state = ConnecionState.CLOSED

    async def send(self, *, text_data: str = None, bytes_data: bytes = None):
        """Only one of the two parameters: `text_data` and `bytes_data` must be
        non-`None`."""
        if self.connection_state != ConnecionState.OPENED:
            msg = "Unexpected call to send to closed connection"
            raise RuntimeError(msg)

        if text_data and bytes_data:
            msg = "Only one of the two parameters: text_data and bytes_data must be non-None."
            raise ValueError(msg)

        await self.asgi_send(
            {"type": "websocket.send", "bytes": bytes_data, "text": text_data}
        )

    async def send_text(self, data: str):
        await self.send(text_data=data)

    async def send_bytes(self, data: bytes):
        await self.send(bytes_data=data)

    async def send_json(
        self, data: t.Any, mode: t.Literal["text"] | t.Literal["bytes"] = "text"
    ):
        if mode not in _MSG_MODES:
            err = f"Expected mode to be one of {_MSG_MODES}. Found={mode}"
            raise RuntimeError(err)

        data = json.dumps(data)

        if mode == "text":
            await self.send(text_data=data)
        else:
            data = data.encode("utf-8")
            await self.send(bytes_data=data)

    async def receive(self):
        if self.connection_state == ConnecionState.CLOSED:
            err = "Unexpected call to receive on a closed connection"
            raise RuntimeError(err)

        msg = await self.asgi_receive()
        msg_type = msg["type"]

        if self.connection_state == ConnecionState.CONNECTING:
            if msg_type != "websocket.connect":
                err = 'Expected "websocket.connect" ASGI message type. got="%s"'
                raise RuntimeError(err % (msg_type))

        elif self.connection_state == ConnecionState.OPENED:
            if msg_type not in ["websocket.receive", "websocket.disconnect"]:
                err = 'Expceted either "websocket.receive" or "websocket.disconnect" ASGI message type. got="%s"'
                raise RuntimeError(err % (msg_type))

            if msg_type == "websocket.disconnect":
                self.connection_state = ConnecionState.CLOSED

        return msg

    async def receive_text(self):
        if self.connection_state != ConnecionState.OPENED:
            msg = "WebSocket conncection must be opened to receive text."
            raise RuntimeError(msg)

        msg = await self.receive()
        return msg["text"]

    async def receive_bytes(self):
        if self.connection_state != ConnecionState.OPENED:
            msg = "WebSocket conncection must be opened to receive bytes."
            raise RuntimeError(msg)

        msg = await self.receive()
        return msg["bytes"]

    async def receive_json(self, mode: t.Literal["text"] | t.Literal["bytes"] = "text"):
        if mode not in _MSG_MODES:
            err = f"Expected mode to be one of {_MSG_MODES}. Found={mode}"
            raise RuntimeError(err)

        msg = await self.receive()

        if mode == "text":
            text = msg["text"]
        else:
            text = msg["bytes"].decode("utf-8")

        return json.loads(text)
