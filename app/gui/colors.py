import json
import os
from pathlib import Path

from .util import *


START_COLORS = {
    "Board": {
        "LightSquares": "#ffe0bf",
        "DarkSquares": "#4f3315",

        "LightPiece": "#ffeedb",
        "DarkPiece": "#211509",

        "PassiveMoveHighlight": "#00ffb3",
        "AggressiveMoveHighlight": "#ff0000",
    },
    "Window": {
        "FirstBackgroundColor": "#ebebeb",
        "SecondBackgroundColor": "#bfbfbf",

        "BorderColor": "#636363",
    },
    "Interface": {
        "TextColor": "#000000"
    }
}


class Colors:
    def __init__(self):
        _directory_path = Path(USER_DATA_DIRECTORY_PATH)
        _file_path      = Path(USER_DATA_DIRECTORY_PATH + COLOR_FILE)

        # Checking to see if directory exists
        if not _directory_path.exists():
            os.mkdir(USER_DATA_DIRECTORY_PATH)

        if not _file_path.exists():
            with open(_file_path, "w") as f:
                json.dump(START_COLORS, f, indent=4, sort_keys=False)

        # Get Color Dictionary
        with open(_file_path, "r") as f:
            self._dictionary: dict = json.load(f)

    # Main window colors
    @property
    def first_background_color(self):
        return self._dictionary["Window"]["FirstBackgroundColor"]

    @property
    def second_background_color(self):
        return self._dictionary["Window"]["SecondBackgroundColor"]

    @property
    def border_color(self):
        return self._dictionary["Window"]["BorderColor"]

    # Board Colors
    @property
    def light_board_color(self):
        return self._dictionary["Board"]["LightSquares"]

    @property
    def dark_board_color(self):
        return self._dictionary["Board"]["DarkSquares"]

    @property
    def light_piece(self):
        return self._dictionary["Board"]["LightPiece"]

    @property
    def dark_piece(self):
        return self._dictionary["Board"]["DarkPiece"]

    @property
    def passive_move_highlight(self):
        return self._dictionary["Board"]["PassiveMoveHighlight"]

    @property
    def aggressive_move_highlight(self):
        return self._dictionary["Board"]["AggressiveMoveHighlight"]

    # Interface Options
    @property
    def text_color(self):
        return self._dictionary["Interface"]["TextColor"]
