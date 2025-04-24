import tkinter as tk
from threading import Thread

from shobu import *

from .canvas import ShobuCanvas
from .info   import InfoFrame
from .colors import Colors

from ..engine import Engine

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # User Data
        self.colors = Colors()

        # Presets
        self.title("Shobu Engine")
        self.geometry("1000x500")
        self.resizable(False, False)
        self.minsize(560, 280)
        self.configure(bg=self.colors.first_background_color)

        self.grid_columnconfigure(0, weight=1, uniform="half")
        self.grid_columnconfigure(1, weight=1, uniform="half")
        self.grid_rowconfigure(0, weight=1)

        # Base Widgets
        self.canvas = ShobuCanvas(self, self.colors, width="500", height="500")
        self.canvas.grid(row=0, column=0, sticky="NSEW")

        self.data_frame = InfoFrame(self, self.colors, width="500", height="500")
        self.data_frame.grid(row=0, column=1, sticky="NSEW")

        # Shobu Based Info
        self.board: Board = Board()

        self.engine = Engine()

        self.engine_player: int = Board.WHITE

    def mainloop(self, n = 0):
        def update_board(t, top_eval, past_serial):
            new_serial = past_serial

            if self.board.has_winner():
                if t > 2000:
                    self.board.reset()
                    t = 0

            elif past_serial != self.board.serialized_string or (self.board.current_player_turn == self.engine_player and t > 60):
                if t > 100:
                    self.data_frame.update_info(self.board, top_eval, "Thinking. . .")
                    t = 0

                else:
                    top_move, top_eval = self.engine.get_best_move(self.board, 2, threads=24)

                    if self.board.current_player_turn == self.engine_player:
                        self.board.make_move(top_move)

                    new_serial = self.board.serialized_string
                    self.data_frame.update_info(self.board, top_eval, "Your Move")
            else:
                t += 33

            self.canvas.update_board(self.board)
            self.canvas.render(self.board)

            self.after(33, lambda: update_board(t, top_eval, new_serial))

        self.data_frame.update_info(self.board, 0.0, "Your Move")
        Thread(target=update_board, args=(0, self.engine.analyze(self.board), self.board.serialized_string)).start()

        super().mainloop(n)
