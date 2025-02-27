from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Player:
    symbol: Literal["X", "O"]


@dataclass(frozen=True)
class Square:
    value: Literal[" ", "X", "O"] = " "


@dataclass(frozen=True)
class Board:
    grid: tuple[
        tuple[Square, Square, Square],
        tuple[Square, Square, Square],
        tuple[Square, Square, Square],
    ] = (
        (Square(), Square(), Square()),
        (Square(), Square(), Square()),
        (Square(), Square(), Square()),
    )

    # def __eq__(self, other):
    #     return self.squares == other.squares

    def __str__(self) -> str:
        rows = []
        for row in self.grid:
            rows.append("│ " + " │ ".join([str(square.value) for square in row]) + " │")
        return (
            "┌───┬───┬───┐\n"
            f"{rows[0]}\n"
            "├───┼───┼───┤\n"
            f"{rows[1]}\n"
            "├───┼───┼───┤\n"
            f"{rows[2]}\n"
            "└───┴───┴───┘"
        )

    def render(self) -> str:
        """TODO: remove this? let caller str(board) or print(board)?"""
        return str(self)


@dataclass(frozen=True)
class Game:
    board: Board = Board()
    players: tuple[Player, Player] = Player("X"), Player("O")
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


def main() -> None:
    new_game = TicTacToe().new_game()
    print(new_game.board)
    print(new_game.board.render())
    print(new_game.players)
    print(new_game.current_player)
    print(new_game.winner)


if __name__ == "__main__":
    main()
