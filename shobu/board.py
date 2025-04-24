import math
from typing import Self

import numpy as np

from shobu.move import Cord, Move, MovePair


class Board:
    # Board / Turn values
    _NO_PIECE:    int =  0
    _BLACK_PIECE: int =  1
    _WHITE_PIECE: int = -1

    NONE:  int        =  0
    BLACK: int        =  1
    WHITE: int        = -1

    # Used for getting legal moves
    _DIRECTIONS = (
        [-1,  1], [0,  1], [1,  1],
        [-1,  0],          [1,  0],
        [-1, -1], [0, -1], [1, -1]
    )
    _MAGNITUDES = {1, 2}

    def __init__(self, serialized_string: str = ""):
        self._boards: dict[str, np.array] = {
            "blackLeft":  None,
            "blackRight": None,
            "whiteLeft":  None,
            "whiteRight": None
        }

        # Tracking number of turns and current player
        self._current_player = self.BLACK
        self._turn_number: float = 1

        self._move_stack: list[tuple[MovePair, str]] = []

        self._winner = None

        # Setting board up (Default if serialized string is empty, otherwise set it up to that position
        self.reset()

        if serialized_string != "":
            # Splitting up the metadata (Board content, turn number, current player turn
            meta_split = serialized_string.split("&&")

            # Setting meta game data
            self._turn_number = float(meta_split[1])
            self._current_player = int(meta_split[2])

            # Extracting the board positions from the string (4 sub boards with arrays that are ints)
            parsed_sub_boards = [[int(x) for x in s.split(';')] for s in meta_split[0].split("||")]

            # Setting each piece into it's square
            for i, sub_board_values in enumerate(parsed_sub_boards):
                sub_board = list(self._boards.keys())[i]
                for j in range(len(sub_board_values)):
                    x = j % 4
                    y = j // 4

                    self._boards[sub_board][x][y] = sub_board_values[j]

    def reset(self) -> None:
        """
        Resets the boards to the start position.
        """
        for board in self._boards:
            # Setting up a 4x4 board
            self._boards[board] = np.array([
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
            ])

        self._current_player = Board.BLACK
        self._turn_number = 1
        self._move_stack.clear()

    def load(self, serial):
        # Splitting up the metadata (Board content, turn number, current player turn
        meta_split = serial.split("&&")

        # Setting meta game data
        self._turn_number = float(meta_split[1])
        self._current_player = int(meta_split[2])

        # Extracting the board positions from the string (4 sub boards with arrays that are ints)
        parsed_sub_boards = [[int(x) for x in s.split(';')] for s in meta_split[0].split("||")]

        # Setting each piece into it's square
        for i, sub_board_values in enumerate(parsed_sub_boards):
            sub_board = list(self._boards.keys())[i]
            for j in range(len(sub_board_values)):
                x = j % 4
                y = j // 4

                self._boards[sub_board][x][y] = sub_board_values[j]

    @staticmethod
    def _get_adjacent_boards(board: str) -> tuple[str, str]:
        is_black: bool = "black" in board
        is_left: bool  = "Left" in board

        opposite_side_board = ("black" if is_black else "white") + ("Right" if is_left else "Left")
        opposite_color_board = ("white" if is_black else "black") + ("Left" if is_left else "Right")

        return opposite_side_board, opposite_color_board
    def _get_opposite_color(self, color: WHITE or BLACK) -> WHITE or BLACK:
        return self.WHITE if color == self.BLACK else self.BLACK

    def has_winner(self) -> bool:
        for sub_board in self._boards:
            if np.sum(self._boards[sub_board] == Board.BLACK) == 0:
                self._winner = self.BLACK
                return True

            elif np.sum(self._boards[sub_board] == Board.WHITE) == 0:
                self._winner = self.WHITE
                return True

        return False

    def make_move(self, move: MovePair):
        self._turn_number += 0.5

        # Making Passive move (Setting previous location to nothing, and moving it to new one)
        passive_piece: str = self._boards[move.passive_board][move.passive_move.start.x][move.passive_move.start.y]

        self._boards[move.passive_board][move.passive_move.start.x][move.passive_move.start.y] = self._NO_PIECE
        self._boards[move.passive_board][move.passive_move.end.x][move.passive_move.end.y] = passive_piece

        # Aggressive move (Moving previous piece to new position, and pushing any pieces)
        pushed_to_cord = move.aggressive_move.end + move.aggressive_move.normalized_difference
        moving_piece = self._boards[move.aggressive_board][move.aggressive_move.start.x][move.aggressive_move.start.y]

        end_piece = self._boards[move.aggressive_board][move.aggressive_move.end.x][move.aggressive_move.end.y]

        if move.aggressive_move.magnitude == 2:
            # Getting the middle cord that the moving piece passes through
            middle_cord  = move.aggressive_move.start + move.aggressive_move.normalized_difference
            middle_piece = self._boards[move.aggressive_board][middle_cord.x][middle_cord.y]

            # Moving the piece, and emptying the middle piece
            self._boards[move.aggressive_board][move.aggressive_move.start.x][move.aggressive_move.start.y] = self._NO_PIECE
            self._boards[move.aggressive_board][middle_cord.x][middle_cord.y] = self._NO_PIECE
            self._boards[move.aggressive_board][move.aggressive_move.end.x][move.aggressive_move.end.y] = moving_piece

            if pushed_to_cord.valid and (middle_piece != self.NONE or end_piece != self.NONE):
                self._boards[move.aggressive_board][pushed_to_cord.x][pushed_to_cord.y] = middle_piece if middle_piece != self._NO_PIECE else end_piece

        else:
            self._boards[move.aggressive_board][move.aggressive_move.start.x][move.aggressive_move.start.y] = self._NO_PIECE
            self._boards[move.aggressive_board][move.aggressive_move.end.x][move.aggressive_move.end.y] = moving_piece

            if end_piece != self._NO_PIECE and pushed_to_cord.valid:
                self._boards[move.aggressive_board][pushed_to_cord.x][pushed_to_cord.y] = end_piece

        # Switching whose turn it is
        self._current_player *= -1 # This just swaps it

        # Updating history
        self._move_stack.append((move, self.serialized_string))

    def undo_move(self):
        self.load(self._move_stack[-1][1])

        self._move_stack.pop()

    def get_legal_moves(self):
        board_color_key: str = "black" if self._current_player == self.BLACK else "white"

        # Getting passive moves that cannot interfere with other pieces, and can only be played on your own board
        passive_moves: list[tuple[Move, str]] = []
        for board in [board_color_key + "Left", board_color_key + "Right"]:
            for x in range(4):
                for y in range(4):
                    # Getting location of piece if it is desired color
                    if self._boards[board][x][y] == self._current_player:
                        start: Cord = Cord(x, y)

                        # Testing directions to see if they are (A) Blocked by a piece (B) Out of bounds
                        # If it is valid, adding it to the list of passive moves that are viable
                        for direction in self._DIRECTIONS:
                            for magnitude in self._MAGNITUDES:
                                end: Cord = start + Cord(direction[0] * magnitude, direction[1] * magnitude)

                                if not end.valid:
                                    continue

                                if magnitude == 1:
                                    if self._boards[board][end.x][end.y] == self._NO_PIECE:
                                        passive_moves.append((Move(start, end), board))

                                else:
                                    middle: Cord = start + Cord(direction[0], direction[1])
                                    if self._boards[board][end.x][end.y] == self._NO_PIECE and self._boards[board][middle.x][middle.y] == self._NO_PIECE:
                                        passive_moves.append((Move(start, end), board))

        moves: list[MovePair] = []
        for passive in passive_moves:
            adjacent_boards = self._get_adjacent_boards(passive[1])

            for board in adjacent_boards:
                for x in range(4):
                    for y in range(4):
                        if self._boards[board][x][y] == self._current_player:
                            start: Cord = Cord(x, y)
                            end: Cord = start + passive[0].difference

                            if not end.valid: # If move is out of bounds for this new piece, move on
                                continue

                            move: MovePair = MovePair(
                                passive[0], # Passive Move
                                Move(start, end), # Aggressive Move
                                passive[1], # Passive Board
                                board, # Aggressive Board
                            )

                            if abs(passive[0].difference.x) == 1 or abs(passive[0].difference.y) == 1:
                                if self._boards[board][end.x][end.y] == self._NO_PIECE: # Empty Square being moved to
                                    moves.append(move)

                                elif self._boards[board][end.x][end.y] == self._get_opposite_color(self._current_player): # An opposite color piece is being attacked
                                    behind_attacked_piece: Cord = end + passive[0].difference

                                    if not behind_attacked_piece.valid: # If there is no more board after it, it can be pushed off
                                        moves.append(move)

                                    elif self._boards[board][behind_attacked_piece.x][behind_attacked_piece.y] == self._NO_PIECE: # If there is empty space behind it, it can be pushed there
                                        moves.append(move)

                            else:
                                after_end: Cord = end + passive[0].normalized_difference

                                destination: str = self._boards[board][end.x][end.y]
                                middle: str = self._boards[board][start.x + passive[0].normalized_difference.x][start.y + passive[0].normalized_difference.y]

                                if destination == self._NO_PIECE and middle == self._NO_PIECE: # Checking to see if no pieces are in the way
                                    moves.append(move)

                                elif middle == self._current_player or destination == self._current_player: # Checking if a single piece of your own color is in the way
                                    continue

                                elif (middle == self._get_opposite_color(self._current_player)) ^ (destination == self._get_opposite_color(self._current_player)): # Checking to see if there is only one opposite colored piece in the way
                                    if not after_end.valid or self._boards[board][after_end.x][after_end.y] == self._NO_PIECE: # Seeing if it gets pushed to open space, or off the board
                                        moves.append(move)

        return moves

    def get_mock(self, move: MovePair, keep_metadata: bool = True, keep_moves: bool = False):
        mock = self.copy(keep_metadata=keep_metadata, keep_moves=keep_moves)

        mock.make_move(move)

        return mock

    def copy(self, keep_moves: bool = False, keep_metadata: bool = True) -> Self:
        # Create a new board without using the serialized string
        new_board = Board()

        # Transferring over other data that isn't board position
        if keep_metadata:
            new_board._turn_number = self._turn_number
            new_board._winner = self._winner
        new_board._current_player = self._current_player

        if keep_moves:
            new_board._move_stack = self._move_stack.copy()

        # Deep copy the boards
        new_board._boards = {
            key: np.copy(value) for key, value in self._boards.items()
        }

        return new_board

    @property
    def boards(self) -> dict[str, np.array]:
        return self._boards

    @property
    def board_keys(self) -> dict.keys:
        return self._boards.keys()

    @property
    def current_player_turn(self) -> int:
        return self._current_player

    @property
    def turn_number(self) -> int:
        return math.floor(self._turn_number)

    @property
    def moves_made(self) -> list[MovePair]:
        return [move[0] for move in self._move_stack]

    @property
    def last_move(self) -> MovePair:
        return self.moves_made[-1]

    @property
    def history(self):
        return [serial[1] for serial in self._move_stack]

    @property
    def winner(self) -> None or int:
        return self._winner

    @property
    def serialized_string(self):
        end_string = ""
        for sub_board in self._boards:
            for y in range(4):
                for x in range(4):
                    end_string += str(self._boards[sub_board][x][y]) + ";"

            end_string = end_string.rstrip(";") + "||"

        end_string = end_string.rstrip("||") + "&&" + str(self._turn_number) + "&&" + str(self._current_player)

        return end_string

    @staticmethod
    def get_player_turn_from_serial(serial: str):
        return int(serial.split("&&")[-1])

    def __copy__(self):
        return Board(self.serialized_string)

    def __str__(self):
        """
        Returns a formatted string representation of the board.
        The board is displayed such that the bottom is on the bottom and the top is on the top.
        Integer values are replaced as:
        -1 -> 'W', 1 -> 'B', 0 -> '.'
        """

        def format_piece(val):
            return str(val).replace("0", ".").replace("-1", "W").replace("1", "B")

        def get_column_strings(half_board):
            # Transpose the 4x4 board and reverse columns to turn them upright
            return [[format_piece(half_board[x][y]) for x in range(3, -1, -1)] for y in reversed(range(4))]

        white_left = get_column_strings(self._boards["whiteLeft"])
        white_right = get_column_strings(self._boards["whiteRight"])
        black_left = get_column_strings(self._boards["blackLeft"])
        black_right = get_column_strings(self._boards["blackRight"])

        def join_rows(left_half, right_half):
            return [f"{' '.join(left)} | {' '.join(right)}" for left, right in zip(left_half, right_half)]

        white_rows = join_rows(white_left, white_right)
        black_rows = join_rows(black_left, black_right)

        return "\n".join(white_rows + ["--------+--------"] + black_rows)
