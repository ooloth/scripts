from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Player:
    symbol: Literal["X", "O"]


@dataclass(frozen=True)
class Square:
    value: str = " "


@dataclass(frozen=True)
class Board:
    grid: tuple[tuple[Square, Square, Square]] = (
        (Square(), Square(), Square()),
        (Square(), Square(), Square()),
        (Square(), Square(), Square()),
    )

    # def __eq__(self, other):
    #     return self.squares == other.squares

    def __str__(self):
        rows = []
        for row in self.grid:
            rows.append("│ " + " │ ".join([square.value for square in row]) + " │")
        return (
            "┌───┬───┬───┐\n"
            f"{rows[0]}\n"
            "├───┼───┼───┤\n"
            f"{rows[1]}\n"
            "├───┼───┼───┤\n"
            f"{rows[2]}\n"
            "└───┴───┴───┘"
        )

    def render(self):
        return str(self)


@dataclass(frozen=True)
class Game:
    board: Board | None = Board()
    players: tuple[Player] = Player("X"), Player("O")
    current_player: Player | None = Player("X")  # need this? track in Player?
    winner: Player | None = None


@dataclass(frozen=True)
class TicTacToe:
    def new_game(self) -> Game:
        """Start a new game with an empty board."""
        return Game()

    def load_game(self, board: Board) -> Game:
        """Load an existing game with a given board."""
        return Game(board=board)
