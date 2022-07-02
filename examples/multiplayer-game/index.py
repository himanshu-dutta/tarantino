import json
import asyncio
from typing import Dict, Tuple

from tarantino import Tarantino
from tarantino.websocket import WSConnection
from tarantino.http import HTMLResponse, HTTPStatusCode, HTTPRequest

import game as ttt

app = Tarantino("tic-tac-toe")

_player_registry: Dict[str, Tuple[ttt.Player, WSConnection]] = dict()
_game_registry = dict()


@app.register_route("/")
async def index(request: HTTPRequest):
    with open("./index.html") as fl:
        body = fl.read()

    return HTMLResponse(body, HTTPStatusCode.STATUS_200_OK)


class GAME_METHODS:
    CONNECT = "connect"
    CREATE_GAME = "create"
    PLAY = "play"
    UPDATE = "update"
    JOIN = "join"


def setInterval(cb, sec):
    async def _inner():
        while True:
            await asyncio.sleep(sec)
            await cb()

    task = asyncio.create_task(_inner())
    return task.cancel


def get_send_update(game: ttt.TicTacToe):
    async def _inner():
        if game.completed:
            _, updateCancelFn = _game_registry[game.game_id]
            updateCancelFn()

        gameObj = game.serialize()
        gameWinState = game.check_win(serialize=True)
        payload = {
            "method": GAME_METHODS.UPDATE,
            "success": True,
            "game": gameObj,
            "winState": gameWinState,
        }
        for player in game.players.values():
            _, conn = _player_registry[player.player_id]
            await conn.send(text_data=json.dumps(payload))

    return _inner


@app.register_route("/game", protocol="websocket")
async def game(conn: WSConnection):
    await conn.accept()

    updateCancelFn = None

    while True:
        msg = await conn.receive()
        if msg["type"] == "websocket.disconnect":
            if updateCancelFn:
                updateCancelFn()
                updateCancelFn = None
            break

        msg = json.loads(msg["text"])
        method = msg["method"]

        print("Request: ", msg)

        if method == GAME_METHODS.CONNECT:
            player = ttt.Player(msg["playerName"])
            _player_registry[player.player_id] = (player, conn)

            payload = {
                "method": GAME_METHODS.CONNECT,
                "success": True,
                "playerId": player.player_id,
            }

        elif method == GAME_METHODS.CREATE_GAME:
            player_id = msg["playerId"]
            player, _ = _player_registry[player_id]
            game = ttt.TicTacToe()
            game.add_player(player)

            send_update = get_send_update(game)
            updateCancelFn = setInterval(send_update, 0.5)

            _game_registry[game.game_id] = (game, updateCancelFn)

            payload = {
                "method": GAME_METHODS.CREATE_GAME,
                "success": True,
                "gameId": game.game_id,
            }

        elif method == GAME_METHODS.JOIN:
            player_id = msg["playerId"]
            game_id = msg["gameId"]
            game, _ = _game_registry[game_id]
            player, _ = _player_registry.get(player_id, (None, None))

            if not player:
                payload = {
                    "method": GAME_METHODS.JOIN,
                    "success": False,
                    "msg": "Invalid player id.",
                }
            else:
                try:
                    game.add_player(player)
                    payload = {
                        "method": GAME_METHODS.JOIN,
                        "success": True,
                        "gameId": game_id,
                    }
                except Exception as e:
                    payload = {
                        "method": GAME_METHODS.JOIN,
                        "success": False,
                        "msg": str(e),
                    }

        elif method == GAME_METHODS.PLAY:
            player_id = msg["playerId"]
            game_id = msg["gameId"]
            cell = msg["cell"]
            game, _ = _game_registry[game_id]

            try:
                game.play(player_id, cell[0], cell[1])
                payload = {"method": GAME_METHODS.PLAY, "success": True}
            except Exception as e:
                payload = {"method": GAME_METHODS.PLAY, "success": False, "msg": str(e)}

        print("Response: ", payload)
        await conn.send(text_data=json.dumps(payload))
