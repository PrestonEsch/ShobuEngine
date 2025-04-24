import tkinter as tk

import shobu
from shobu import Board


class InfoFrame(tk.Frame):
    def __init__(self, master, colors, *args, **kwargs):
        super().__init__(master, bg=colors.first_background_color, *args, **kwargs)

        self.root   = master
        self.colors = colors

        # Config
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # Amount of turns so far
        self.turns_title = tk.Label(self, text="Turn Number:", font=("", 24), foreground=self.colors.text_color, background=self.colors.first_background_color)
        self.turns_title.grid(row=6, column=0, sticky="NSEW")

        self.turns_value = tk.Label(self, text="0", font=("", 24), foreground=self.colors.text_color, background=self.colors.first_background_color)
        self.turns_value.grid(row=6, column=1, sticky="NSEW")

        # Status
        self.status_title = tk.Label(self, text="Status:", font=("", 24), foreground=self.colors.text_color,
                                    background=self.colors.first_background_color)
        self.status_title.grid(row=3, column=0, sticky="NSEW")

        self.status_value = tk.Label(self, text="Waiting", font=("", 24), foreground=self.colors.text_color,
                                    background=self.colors.first_background_color)
        self.status_value.grid(row=3, column=1, sticky="NSEW")

        # Current Player Turn
        self.player_turn_title = tk.Label(self, text="Player's Turn:", font=("", 24), foreground=self.colors.text_color,
                                    background=self.colors.first_background_color)
        self.player_turn_title.grid(row=5, column=0, sticky="NSEW")

        self.player_turn_value = tk.Label(self, text="0", font=("", 24), foreground=self.colors.text_color,
                                    background=self.colors.first_background_color)
        self.player_turn_value.grid(row=5, column=1, sticky="NSEW")

        # Current Eval
        self.eval_title = tk.Label(self, text="Position Evaluation:", font=("", 24), foreground=self.colors.text_color, background=self.colors.first_background_color)
        self.eval_title.grid(row=0, column=0, sticky="NSEW")

        self.eval_value = tk.Label(self, text="0.0", font=("", 24), foreground=self.colors.text_color, background=self.colors.first_background_color)
        self.eval_value.grid(row=0, column=1, sticky="NSEW")

        # Current Eval
        def update_player(*_args):
            print(f"Engine is now playing: {self.engine_player_var.get()}")

            if self.engine_player_var.get() == "White":
                self.root.engine_player = Board.WHITE

            elif self.engine_player_var.get() == "Black":
                self.root.engine_player = Board.BLACK

            else:
                self.root.engine_player = Board.NONE

        self.engine_player_var = tk.StringVar(master)
        self.engine_player_var.set("White")

        self.engine_player_title = tk.Label(self, text="Engine Plays:", font=("", 24), foreground=self.colors.text_color,
                                   background=self.colors.first_background_color)
        self.engine_player_title.grid(row=4, column=0, sticky="NSEW")

        self.engine_player_dropdown = tk.OptionMenu(self, self.engine_player_var, *["White", "Black", "None"], command=update_player)
        self.engine_player_dropdown.config(font=("", 24))
        self.engine_player_dropdown.grid(row=4, column=1, sticky="NSEW")

    def update_info(self, board: shobu.Board, current_eval: float, status: str):
        self.turns_value.configure(text=board.turn_number)

        self.eval_value.configure(text=str(round(current_eval, 4) if isinstance(current_eval, float) else current_eval))
        self.player_turn_value.configure(text="Black" if board.current_player_turn == board.BLACK else "White")
        self.status_value.configure(text=status)
