"""
TODO:
- [ ] ...
"""

import textwrap

from tic_tac_toe.play import Board, Player, Square, TicTacToe


class TestNewGame:
    def test_board_is_empty(_) -> None:
        game = TicTacToe().new_game()
        assert all(square.value == " " for row in game.board.grid for square in row)

    def test_there_are_two_players(_) -> None:
        game = TicTacToe().new_game()
        assert game.players == (Player("X"), Player("O"))

    def test_player_x_goes_first(_) -> None:
        game = TicTacToe().new_game()
        assert game.current_player == Player("X")


class TestRenderBoard:
    def test_empty_board_renders_correctly(_) -> None:
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

    def test_populated_board_renders_correctly(_) -> None:
        board = Board([
            [Square("X"), Square(" "), Square("O")],
            [Square(" "), Square("O"), Square(" ")],
            [Square(" "), Square(" "), Square("X")],
        ])
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


class TestOfferMoves:
    def test_when_board_is_empty_all_squares_are_offered(_) -> None:
        game = TicTacToe().new_game()
        choices = game.offer_choices()
        assert choices == [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

    def test_when_board_is_full_no_squares_are_offered(_) -> None:
        board = Board([
            [Square("X"), Square("O"), Square("X")],
            [Square("X"), Square("O"), Square("O")],
            [Square("O"), Square("X"), Square("X")],
        ])
        game = TicTacToe().load_game(board=board)
        choices = game.offer_choices()
        assert choices == []

    def test_when_board_is_partially_full_only_empty_squares_are_offered(_) -> None:
        board = Board([
            [Square("X"), Square("O"), Square("X")],
            [Square("X"), Square(" "), Square("O")],
            [Square("O"), Square("X"), Square("X")],
        ])
        game = TicTacToe().load_game(board=board)
        choices = game.offer_choices()
        assert choices == [(1, 1)]
