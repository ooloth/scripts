"""
TODO:
- [ ] ...
"""

import textwrap

from tic_tac_toe.play import Board, Player, Square, TicTacToe


class TestGame:
    def test_new_game_starts_with_empty_board(_) -> None:
        game = TicTacToe().new_game()
        assert all(square.value == " " for row in game.board.grid for square in row)

    def test_new_game_starts_with_two_players(_) -> None:
        game = TicTacToe().new_game()
        assert game.players == (Player("X"), Player("O"))

    def test_new_game_starts_with_player_x_going_first(_) -> None:
        game = TicTacToe().new_game()
        assert game.current_player == Player("X")


class TestBoard:
    def test_board_renders_correctly_when_empty(_) -> None:
        game = TicTacToe().new_game()
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

        assert game.board.render() == expected

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
