"""
TODO:
- [ ] ...
"""

import textwrap

from tic_tac_toe.play import Board, Player, Square, TicTacToe


def test_when_game_starts_board_is_empty() -> None:
    new_game = TicTacToe().new_game()
    assert all(square.value == " " for row in new_game.board.grid for square in row)


def test_when_game_starts_there_are_two_players() -> None:
    new_game = TicTacToe().new_game()
    assert new_game.players == (Player("X"), Player("O"))


def test_when_game_starts_player_x_goes_first() -> None:
    new_game = TicTacToe().new_game()
    assert new_game.current_player == Player("X")


def test_board_renders_correctly_when_empty() -> None:
    new_game = TicTacToe().new_game()
    expected = textwrap.dedent(
        """
        ┌───┬───┬───┐
        │   │   │   │
        ├───┼───┼───┤
        │   │   │   │
        ├───┼───┼───┤
        │   │   │   │
        └───┴───┴───┘
        """
    ).strip()

    assert new_game.board.render() == expected


def test_board_renders_correctly_when_populated() -> None:
    board = Board((
        (Square("X"), Square(" "), Square("O")),
        (Square(" "), Square("O"), Square(" ")),
        (Square(" "), Square(" "), Square("X")),
    ))
    game = TicTacToe().load_game(board=board)

    expected = textwrap.dedent(
        """
        ┌───┬───┬───┐
        │ X │   │ O │
        ├───┼───┼───┤
        │   │ O │   │
        ├───┼───┼───┤
        │   │   │ X │
        └───┴───┴───┘
        """
    ).strip()

    assert game.board.render() == expected
