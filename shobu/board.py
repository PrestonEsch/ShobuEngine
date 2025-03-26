from shobu.move import Cord, Move, MovePair


class Board:
    _NO_PIECE    = "."
    _BLACK_PIECE = "B"
    _WHITE_PIECE = "W"

    BLACK = "B"
    WHITE = "W"

    _boards: dict[str, list] = {
        "blackLeft":  [],
        "blackRight": [],
        "whiteLeft":  [],
        "whiteRight": []
    }

    _DIRECTIONS = [
        [-1,  1], [0,  1], [1,  1],
        [-1,  0],          [1,  0],
        [-1, -1], [0, -1], [1, -1]
    ]
    _MAGNITUDES = [1, 2]

    def __init__(self):
        self._winner = None

        self.reset()

    def reset(self) -> None:
        """
        Resets the boards to the start position.
        """
        for board in self._boards:
            # Setting up a 4x4 board
            self._boards[board] = [
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
                [self._BLACK_PIECE, self._NO_PIECE, self._NO_PIECE, self._WHITE_PIECE],
            ]

    @staticmethod
    def _get_adjacent_boards(board: str) -> tuple[str, str]:
        is_black: bool = "black" in board
        is_left: bool  = "Left" in board

        opposite_side_board = ("black" if is_black else "white") + ("Right" if is_left else "Left")
        opposite_color_board = ("white" if is_black else "black") + ("Left" if is_left else "Right")

        return opposite_side_board, opposite_color_board
    def _get_opposite_color(self, color: WHITE or BLACK) -> WHITE or BLACK:
        return self.WHITE if color == self.BLACK else self.BLACK

    def is_winner(self) -> bool:
        for board in self._boards:
            black_found: bool = False
            white_found: bool = False
            for x in range(4):
                for y in range(4):
                    if self._boards[board][x][y] is self.BLACK:
                        black_found = True
                    elif self._boards[board][x][y] is self.WHITE:
                        white_found = True

            if not black_found:
                self._winner = self.WHITE
                return True
            elif not white_found:
                self._winner = self.BLACK
                return True
            else:
                self._winner = None

        return False

    @property
    def winner(self) -> None or str:
        return self._winner


    def make_move(self, move: MovePair):
        # Making Passive move (Setting previous location to nothing, and moving it to new one)
        passive_piece: str = self._boards[move.passive_board][move.passive_move.start.x][move.passive_move.start.y]

        self._boards[move.passive_board][move.passive_move.start.x][move.passive_move.start.y] = self._NO_PIECE
        self._boards[move.passive_board][move.passive_move.end.x][move.passive_move.end.y] = passive_piece

        # Aggressive move (Moving previous piece to new position, and pushing any pieces)
        aggressive_piece: str = self._boards[move.aggressive_board][move.aggressive_move.start.x][move.aggressive_move.start.y]
        after_end: Cord = move.aggressive_move.end + move.aggressive_move.normalized_difference # One past the end

        piece_on_end: str = self._boards[move.aggressive_board][move.aggressive_move.end.x][move.aggressive_move.end.y] # Piece that the moving aggressive piece is on

        # Actually just moving the aggressive piece
        self._boards[move.aggressive_board][move.aggressive_move.start.x][move.aggressive_move.start.y] = self._NO_PIECE
        self._boards[move.aggressive_board][move.aggressive_move.end.x][move.aggressive_move.end.y] = aggressive_piece

        if move.aggressive_move.magnitude == 2:
            if piece_on_end != self._NO_PIECE and after_end.valid:
                self._boards[move.aggressive_board][after_end.x][after_end.y] = piece_on_end

            else:
                middle: Cord = move.aggressive_move.start + move.aggressive_move.normalized_difference
                piece_on_middle = self._boards[move.aggressive_board][middle.x][middle.y]

                if piece_on_middle != self._NO_PIECE and after_end.valid:
                    self._boards[move.aggressive_board][after_end.x][after_end.y] = piece_on_end

                self._boards[move.aggressive_board][middle.x][middle.y] = self._NO_PIECE

        elif move.aggressive_move.magnitude == 1: # Logic for pushing a piece when magnitude is 1
            if piece_on_end != self._NO_PIECE and after_end.valid: # Checking to see if a piece was even there, and it has a place to go
                self._boards[move.aggressive_board][after_end.x][after_end.y] = piece_on_end

    def get_legal_moves(self, color: WHITE or BLACK):
        board_color_key: str = "black" if color == self.BLACK else "white"

        # Getting passive moves that cannot interfere with other pieces, and can only be played on your own board
        passive_moves: list[tuple[Move, str]] = []
        for board in [board_color_key + "Left", board_color_key + "Right"]:
            for x in range(4):
                for y in range(4):
                    # Getting location of piece if it is desired color
                    if self._boards[board][x][y] == color:
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
                        if self._boards[board][x][y] == color:
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

                                elif self._boards[board][end.x][end.y] == self._get_opposite_color(color): # An opposite color piece is being attacked
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

                                elif middle == color or destination == color: # Checking if a single piece of your own color is in the way
                                    continue

                                elif (middle == self._get_opposite_color(color)) ^ (destination == self._get_opposite_color(color)): # Checking to see if there is only one opposite colored piece in the way
                                    if not after_end.valid or self._boards[board][after_end.x][after_end.y] == self._NO_PIECE: # Seeing if it gets pushed to open space, or off the board
                                        moves.append(move)

        return moves

    def __str__(self):
        return \
f"""{self._boards["whiteLeft"][0][3]} {self._boards["whiteLeft"][1][3]} {self._boards["whiteLeft"][2][3]} {self._boards["whiteLeft"][3][3]} | {self._boards["whiteRight"][0][3]} {self._boards["whiteRight"][1][3]} {self._boards["whiteRight"][2][3]} {self._boards["whiteRight"][3][3]}
{self._boards["whiteLeft"][0][2]} {self._boards["whiteLeft"][1][2]} {self._boards["whiteLeft"][2][2]} {self._boards["whiteLeft"][3][2]} | {self._boards["whiteRight"][0][2]} {self._boards["whiteRight"][1][2]} {self._boards["whiteRight"][2][2]} {self._boards["whiteRight"][3][2]}
{self._boards["whiteLeft"][0][1]} {self._boards["whiteLeft"][1][1]} {self._boards["whiteLeft"][2][1]} {self._boards["whiteLeft"][3][1]} | {self._boards["whiteRight"][0][1]} {self._boards["whiteRight"][1][1]} {self._boards["whiteRight"][2][1]} {self._boards["whiteRight"][3][1]}
{self._boards["whiteLeft"][0][0]} {self._boards["whiteLeft"][1][0]} {self._boards["whiteLeft"][2][0]} {self._boards["whiteLeft"][3][0]} | {self._boards["whiteRight"][0][0]} {self._boards["whiteRight"][1][0]} {self._boards["whiteRight"][2][0]} {self._boards["whiteRight"][3][0]}
--------+--------
{self._boards["blackLeft"][0][3]} {self._boards["blackLeft"][1][3]} {self._boards["blackLeft"][2][3]} {self._boards["blackLeft"][3][3]} | {self._boards["blackRight"][0][3]} {self._boards["blackRight"][1][3]} {self._boards["blackRight"][2][3]} {self._boards["blackRight"][3][3]}
{self._boards["blackLeft"][0][2]} {self._boards["blackLeft"][1][2]} {self._boards["blackLeft"][2][2]} {self._boards["blackLeft"][3][2]} | {self._boards["blackRight"][0][2]} {self._boards["blackRight"][1][2]} {self._boards["blackRight"][2][2]} {self._boards["blackRight"][3][2]}
{self._boards["blackLeft"][0][1]} {self._boards["blackLeft"][1][1]} {self._boards["blackLeft"][2][1]} {self._boards["blackLeft"][3][1]} | {self._boards["blackRight"][0][1]} {self._boards["blackRight"][1][1]} {self._boards["blackRight"][2][1]} {self._boards["blackRight"][3][1]}
{self._boards["blackLeft"][0][0]} {self._boards["blackLeft"][1][0]} {self._boards["blackLeft"][2][0]} {self._boards["blackLeft"][3][0]} | {self._boards["blackRight"][0][0]} {self._boards["blackRight"][1][0]} {self._boards["blackRight"][2][0]} {self._boards["blackRight"][3][0]}"""
