from tarantino import SubApp
from tarantino.concurrency import set_interval
from tarantino.websocket.handlers import WebsocketHandler

subapp = SubApp(prefix="/chat")


@subapp.websocket("/{username:str}")
class ChatHandler(WebsocketHandler):
    async def send_ping_msg(self):
        print("[Server PING] sending message")
        await self.send(text_data=f"[Server PING]: {self.params['username']}")

    async def on_connect(self):
        print("Connection opened by user: ", self.params["username"])
        await self.accept()
        self.ping_close = await set_interval(self.send_ping_msg, 2)

    async def on_message(self, text_data: str = None, bytes_data: bytes = None):
        print("Msg from WS: ", text_data)
        await self.send(text_data=f"Echo: {text_data}")

    async def on_disconnect(self, code: int):
        print("Close code: ", code)
        self.ping_close()
