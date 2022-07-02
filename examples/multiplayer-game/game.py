import random
from typing import Dict
from uuid import uuid4


WINNING_COMBINATIONS = [
    [
        [0, 0],
        [0, 1],
        [0, 2],
    ],
    [
        [1, 0],
        [1, 1],
        [1, 2],
    ],
    [
        [2, 0],
        [2, 1],
        [2, 2],
    ],
    [
        [0, 0],
        [1, 0],
        [2, 0],
    ],
    [
        [0, 1],
        [1, 1],
        [2, 1],
    ],
    [
        [0, 2],
        [1, 2],
        [2, 2],
    ],
    [
        [0, 0],
        [1, 1],
        [2, 2],
    ],
    [
        [0, 2],
        [1, 1],
        [2, 0],
    ],
]


class SYMBOLS:
    CROSS = "X"
    NAUGHT = "O"
    NONE = "-"


class Player:
    def __init__(self, name: str):
        self.name = name
        self.player_id = uuid4().hex

    def serialize(self):
        return {
            "name": self.name,
            "playerId": self.player_id,
        }


class TicTacToe:
    def __init__(self):
        self.game_id = uuid4().hex
        self.board = [
            [SYMBOLS.NONE, SYMBOLS.NONE, SYMBOLS.NONE],
            [SYMBOLS.NONE, SYMBOLS.NONE, SYMBOLS.NONE],
            [SYMBOLS.NONE, SYMBOLS.NONE, SYMBOLS.NONE],
        ]
        self.players: Dict[str, Player] = dict()
        self._completed = False
        self.curr_symbol = SYMBOLS.CROSS if random.random() > 0.5 else SYMBOLS.NAUGHT

    def add_player(self, player: Player):
        if len(self.players) >= 2:
            raise RuntimeError("Can't add more than 2 players to the game")

        if len(self.players) == 0:
            self.players[
                SYMBOLS.CROSS if random.random() > 0.5 else SYMBOLS.NAUGHT
            ] = player
        else:
            if self.players.get(SYMBOLS.CROSS) is not None:
                self.players[SYMBOLS.NAUGHT] = player
            else:
                self.players[SYMBOLS.CROSS] = player

    def play(self, player_id: str, x: int, y: int):
        if not ((x >= 0 and x <= 2) or (y >= 0 and y <= 2)):
            msg = f"Invalid move location: ({x}, {y})"
            raise RuntimeError(msg)

        if getattr(self.players.get(self.curr_symbol), "player_id", "") == player_id:

            slot = self.board[x][y]

            if slot != SYMBOLS.NONE:
                msg = f"Invalid move location: ({x}, {y})"
                raise RuntimeError(msg)

            self.board[x][y] = self.curr_symbol

            self.curr_symbol = (
                SYMBOLS.CROSS if self.curr_symbol == SYMBOLS.NAUGHT else SYMBOLS.NAUGHT
            )
        else:
            msg = f"Invalid player played the move: {player_id}"
            raise RuntimeError(msg)

    @property
    def completed(self):
        if not self._completed:
            for x in range(3):
                for y in range(3):
                    sym = self.board[x][y]
                    if sym == SYMBOLS.NONE:
                        return self._completed

        self._completed = True
        return self._completed

    def check_win(self, serialize=False):
        for comb in WINNING_COMBINATIONS:

            val1 = self.board[comb[0][0]][comb[0][1]]
            val2 = self.board[comb[1][0]][comb[1][1]]
            val3 = self.board[comb[2][0]][comb[2][1]]

            if val1 != SYMBOLS.NONE:
                if val1 == val2 and val2 == val3:
                    self._completed = True
                    winner = self.players[val1]
                    if serialize:
                        winner = winner.serialize()
                    self._completed = True
                    return {"win": True, "winner": winner, "combination": comb}

        return {"win": False}

    def serialize(self):
        o = {
            "gameId": self.game_id,
            "board": self.board,
            "players": {
                sym: player.serialize() for (sym, player) in self.players.items()
            },
            "currentSymbol": self.curr_symbol,
        }

        return o
