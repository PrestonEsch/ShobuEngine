import tkinter as tk

import shobu


class ShobuCanvas(tk.Canvas):
    def __init__(self, master, colors, *args, **kwargs):
        super().__init__(master, borderwidth=0, border=0, highlightthickness=0, background=colors.first_background_color,
                         *args, **kwargs)

        # User Data
        self.colors = colors

        # Render
        self.current_width = 0
        self.current_height = 0

        self.board_size: int = 500
        self.board_start_y: int = 0

        # Input
        self.mouse_position: list[int] = [0, 0]
        self.current_cord: shobu.Cord = shobu.Cord(1, 1)
        self.current_board = shobu.WHITE_LEFT

        # Selected
        self.passive_cords: list[(shobu.Cord, str)] = []
        self.aggressive_cords: list[(shobu.Cord, str)] = []

        # Binding changes to their respective actions (Mouse Moves, Resizing)
        self.bind("<Configure>",       self._on_resize)
        self.bind("<Motion>",          self._on_mouse_move)
        self.bind("<ButtonRelease-1>", self._on_button_up)
        self.bind("<Button-3>",        self._reset_selected)

    def update_board(self, board: shobu.Board):
        if len(self.passive_cords) == 2 and len(self.aggressive_cords) == 2:
            # Create base move to check
            move = shobu.MovePair(
                shobu.Move(self.passive_cords[0][0], self.passive_cords[1][0]),
                shobu.Move(self.aggressive_cords[0][0], self.aggressive_cords[1][0]),
                self.passive_cords[0][1],
                self.aggressive_cords[0][1]
            )

            # Checks to see if move is valid, then makes it
            if move in board.get_legal_moves():
                board.make_move(move)

            else:
                print("Invalid Move:\n" + str(move))

            self._reset_selected()

    def render(self, board: shobu.Board or None = None):
        # Clearing Board
        self.delete(tk.ALL)

        # User Boards
        self._draw_board_quadrant(self.board_size / 2, self.board_size / 2, self.colors.dark_board_color)
        self._draw_board_quadrant(0, self.board_size / 2, self.colors.light_board_color)

        # Bot Boards
        self._draw_board_quadrant(0, 0, self.colors.dark_board_color)
        self._draw_board_quadrant(self.board_size / 2, 0, self.colors.light_board_color)

        # Drawing current move highlights
        for cord in self.passive_cords:
            self._draw_single_square(cord[0].x, cord[0].y, cord[1], self.colors.passive_move_highlight)

        for cord in self.aggressive_cords:
            self._draw_single_square(cord[0].x, cord[0].y, cord[1], self.colors.aggressive_move_highlight)

        # Drawing pieces on
        if board is not None:
            # Basic Variables (Piece circle radius, simple units)
            radius: int = int((self.board_size / 16) * 0.9)
            half_square: int = int(self.board_size / 16)
            full_square: int = int(self.board_size / 8)

            for sub_board in board.boards:
                # Getting the offset for things like left/right, and white/black sides
                sub_board_offset = [0, 0]
                if sub_board.count("black"):
                    sub_board_offset[1] += self.board_size / 2

                if sub_board.count("Right"):
                    sub_board_offset[0] += self.board_size / 2

                # Going through every coordinate in the sub grids
                for x in range(0, 4):
                    for y in range(0, 4):
                        color = None

                        if board.boards[sub_board][3 - x][3 - y] == shobu.Board.BLACK:
                            color = self.colors.dark_piece

                        elif board.boards[sub_board][3 - x][3 - y] == shobu.Board.WHITE:
                            color = self.colors.light_piece

                        # Drawing piece onto board if a color is found
                        if color is not None:
                            center = (
                                sub_board_offset[0] + half_square + (x * full_square),
                                sub_board_offset[1] + half_square + (y * full_square) + self.board_start_y
                            )

                            self.create_oval(center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius,
                                             fill=color)

    def _reset_selected(self, _event = None):
        # Clearing old input options
        self.passive_cords.clear()
        self.aggressive_cords.clear()

    def _on_button_up(self, _event):
        if len(self.passive_cords) < 2:
            # Clearing if user clicks off of board
            if len(self.passive_cords) == 1:
                if self.passive_cords[0][1] != self.current_board:
                    self._reset_selected()
                    return

            self.passive_cords.append((self.current_cord, self.current_board))

        elif len(self.aggressive_cords) < 2:
            # Clearing if user clicks off of board
            if len(self.aggressive_cords) == 1:
                if self.aggressive_cords[0][1] != self.current_board:
                    self._reset_selected()
                    return

            self.aggressive_cords.append((self.current_cord, self.current_board))

    def _on_mouse_move(self, event):
        # Mouse Profiling (Adaptive and Results in [None, None] if mouse is off drawn canvas)
        self.mouse_position[0] = event.x if event.x in range(0, int(self.board_size)) else None
        self.mouse_position[1] = event.y - int((self.current_height - self.board_size) / 2) if event.y in range(int(self.board_start_y), int(self.board_size)) else None
        self.mouse_position = [None, None, -1] if self.mouse_position[0] is None or self.mouse_position[1] is None else self.mouse_position

        # Adjusting cord & board
        if self.mouse_position[0] is not None and self.mouse_position[1] is not None:
            # Getting board location
            self.current_board =  ""
            self.current_board += "black" if self.mouse_position[1] > self.board_size / 2 else "white"
            self.current_board += "Right" if self.mouse_position[0] > self.board_size / 2 else "Left"

            self.current_cord: shobu.Cord = shobu.Cord(3 - int(self.mouse_position[0] / (self.board_size / 8)) % 4,
                                                       3 - int(self.mouse_position[1] / (self.board_size / 8)) % 4)

    def _on_resize(self, event):
        # Store the new dimensions
        self.current_width  = event.width
        self.current_height = event.height

        self.board_size = min(self.current_width, self.current_height)
        self.board_start_y: int = (self.current_height / 2) - (self.board_size / 2)

        self.render()

    def _draw_board_quadrant(self, x_offset, y_offset, color):
        sub_square_size: int = int(self.board_size / 8)
        for precise_x_offset in range(0, sub_square_size * 4, sub_square_size):
            for precise_y_offset in range(0, sub_square_size * 4, sub_square_size):
                square_x = precise_x_offset + x_offset
                square_y = precise_y_offset + y_offset + self.board_start_y

                self.create_rectangle(square_x, square_y, square_x + sub_square_size, square_y + sub_square_size,
                                      fill=color, outline=self.colors.border_color)

    def _draw_single_square(self, x, y, board, color):
        square_size: int = int(self.board_size / 8)

        x = abs(x - 3)
        y = abs(y - 3)

        board_offset: list[int] = [0, 0]
        if board.count("black"):
            board_offset[1] += int(self.board_size / 2)

        if board.count("Right"):
            board_offset[0] += int(self.board_size / 2)

        square_x = x * square_size + board_offset[0]
        square_y = y * square_size + board_offset[1] + self.board_start_y

        self.create_rectangle(square_x, square_y, square_x + square_size, square_y + square_size,
                              fill=color, outline=self.colors.border_color)
