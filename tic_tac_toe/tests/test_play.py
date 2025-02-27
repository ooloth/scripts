"""
TODO:
- [ ] ...
"""

import textwrap

from tic_tac_toe.play import Board, Player, Square, TicTacToe


class TestGame:
    def test_game_starts_with_empty_board(_) -> None:
        new_game = TicTacToe().new_game()
        assert all(square.value == " " for row in new_game.board.grid for square in row)

    def test_game_starts_with_two_players(_) -> None:
        new_game = TicTacToe().new_game()
        assert new_game.players == (Player("X"), Player("O"))

    def test_game_starts_with_player_x_going_first(_) -> None:
        new_game = TicTacToe().new_game()
        assert new_game.current_player == Player("X")


class TestBoard:
    def test_board_renders_correctly_when_empty(_) -> None:
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

    def test_board_renders_correctly_when_populated(_) -> None:
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
