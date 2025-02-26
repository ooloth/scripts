from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Player:
    symbol: Literal["X", "O"]


@dataclass(frozen=True)
class Square:
    pass


@dataclass(frozen=True)
class Board:
    pass


@dataclass(frozen=True)
class Game:
    board: Board | None = Board()
    players: set[Player] = field(default_factory=lambda: {Player("X"), Player("O")})
    current_player: Player | None = Player("X")  # track turn in Player?
    winner: Player | None = None


@dataclass(frozen=True)
class TicTacToe:
    def new_game(self) -> Game:
        return Game()
