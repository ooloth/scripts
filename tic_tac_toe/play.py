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
    board: Board
    # just track one player (the current one)?
    players: tuple[Player, Player] = (Player("X"), Player("O"))
    current_player: Player = Player("X")  # need this? track in Player?
    winner: Player | None = None


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
    print(game.board)
    print(game.board.render())
    print(game.players)
    print(game.current_player)
    print(game.winner)


if __name__ == "__main__":
    main()
