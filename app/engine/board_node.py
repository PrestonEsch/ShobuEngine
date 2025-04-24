from typing import Self

from shobu import Board


class BoardNode:
    def __init__(self, board: Board, board_eval: float or None = None):
        self.board: Board = board
        self.eval: float or None = board_eval

    @property
    def has_eval(self):
        return self.eval is not None

    @property
    def serial(self):
        return self.board.serialized_string

    @staticmethod
    def generate_from_board(board: Board, board_eval: float, keep_metadata: bool = False, keep_moves: bool = False):
        node = BoardNode(board.serialized_string, board_eval)
        node.board = board.copy(keep_metadata=keep_metadata, keep_moves=keep_moves)

        return node

    def __eq__(self, other: Self):
        return self.serial == other.serial

    def __str__(self):
        return f"Turn: {self.board.current_player_turn} | Moves: {self.board.turn_number}\n{self.board}\nEval: {self.eval}"
