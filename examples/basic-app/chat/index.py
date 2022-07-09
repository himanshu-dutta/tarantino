from tarantino import SubApp
from tarantino.websocket import WSConnection

subapp = SubApp(prefix="/chat")


@subapp.websocket("/{username:str}")
async def chat_handler(conn: WSConnection, username: str):
    await conn.accept()

    await conn.send(text_data=f"Client: {username}")

    while True:
        msg = await conn.receive()
        if msg["type"] == "websocket.disconnect":
            return

        print("Msg from ws: ", msg)
        await conn.send(text_data=msg.get("text"))
