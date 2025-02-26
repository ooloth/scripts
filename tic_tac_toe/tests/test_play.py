""" """

from tic_tac_toe.play import Board, Player, TicTacToe


def test_when_game_starts_board_is_empty():
    tic_tac_toe = TicTacToe()
    new_game = tic_tac_toe.new_game()
    new_board = Board()
    assert new_game.board == new_board


def test_when_game_starts_there_are_two_players():
    tic_tac_toe = TicTacToe()
    new_game = tic_tac_toe.new_game()
    assert new_game.players == {Player("X"), Player("O")}


def test_when_game_starts_player_x_goes_first():
    tic_tac_toe = TicTacToe()
    new_game = tic_tac_toe.new_game()
    assert new_game.current_player == Player("X")
