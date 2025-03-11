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
    grid: list[list[Square]]

    # def get_square(self, row: Literal[0, 1, 2], col: Literal[0, 1, 2]) -> Square:
    #     """Avoid this? No getters, no setters?"""
    #     if 0 <= row < 3 and 0 <= col < 3:
    #         return self.grid[row][col]
    #     else:
    #         raise IndexError("Row and column must be in the range 0-2.")

    # def set_square(self, row: Literal[0, 1, 2], col: Literal[0, 1, 2], square: Square) -> None:
    #     """Avoid this? No getters, no setters?"""
    #     if 0 <= row < 3 and 0 <= col < 3:
    #         self.grid[row][col] = square
    #     else:
    #         raise IndexError("Row and column must be in the range 0-2.")

    # def __eq__(self, other):
    #     return self.squares == other.squares

    def render(self) -> str:
        """Represent board as a 3x3 grid of squares."""
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


type Coordinate = tuple[int, int]


@dataclass(frozen=True)
class Game:
    board: Board
    # just track one player (the current one)?
    players: tuple[Player, Player] = (Player("X"), Player("O"))
    current_player: Player = Player("X")  # need this? track in Player?
    winner: Player | None = None

    def offer_choices(self) -> list[Coordinate]:
        """Use capabilities approach to only offer valid choices."""
        return [
            (row_index, col_index)
            for row_index, squares in enumerate(self.board.grid)
            for col_index, square in enumerate(squares)
            if square.value == " "
        ]


@dataclass(frozen=True)
class TicTacToe:
    def new_game(self) -> Game:
        """Start a new game with an empty board."""
        empty_board = Board([list([Square() for _ in range(3)]) for _ in range(3)])
        return Game(board=empty_board)

    def load_game(self, board: Board) -> Game:
        """Load an existing game with a given board."""
        return Game(board=board)


def main() -> None:
    game = TicTacToe().new_game()
    print(game.board.render())


if __name__ == "__main__":
    main()
