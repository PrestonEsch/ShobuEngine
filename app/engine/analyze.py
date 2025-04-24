from pathlib import Path

from shobu import Board

from ..gui.util import MAIN_ENGINE_PROFILE, SAMPLE_PROFILE, ENGINE_PROFILES_DIRECTORY_PATH

import math
import os

import numpy as np

import json


class Analyze:
    _DIRECTIONS: list[tuple[int, int]] = [
        (-1,  1), (0,  1), (1,  1),
        (-1,  0),          (1,  0),
        (-1, -1), (0, -1), (1, -1)
    ]

    _DIRECTION_MAG_OFFSETS = [
        (dx * mag, dy * mag, dx, dy, mag)
        for dx, dy in _DIRECTIONS
        for mag in (1, 2)
    ]

    BLACK_WIN: float = float('inf')
    WHITE_WIN: float = float('-inf')

    def __init__(self, concept_weights: dict[str, float] or None):
        self._concept_weights: [str, float] = {
            "Material":   1.0,
            "Support":    1.0,
            "Mobility":   1.0,
            "Aggression": 1.0
        }

        if concept_weights is not None:
            self.set_concept_weights(concept_weights)

        else:
            _dir = Path(ENGINE_PROFILES_DIRECTORY_PATH)
            _file_path = Path(MAIN_ENGINE_PROFILE)

            # Checking folder path
            if not _dir.exists():
                os.mkdir(_dir)

            # Checking to see if directory exists
            if not _file_path.exists():
                with open(_file_path, "w") as f:
                    json.dump(SAMPLE_PROFILE, f, indent=4, sort_keys=False)

            # Get Color Dictionary
            with open(_file_path, "r") as f:
                self._concept_weights: dict = json.load(f)


    def set_concept_weights(self, concept_weights: dict[str, float]):
        self._concept_weights: [str, float] = {
            "Material": concept_weights["Material"],
            "Support": concept_weights["Support"],
            "Mobility": concept_weights["Mobility"],
            "Aggression": concept_weights["Aggression"]
        }

    @staticmethod
    def _on_board(x, y):
        return x in range(0, 4) and y in range(0, 4)

    def _material_equation(self, n) -> float:
        return (math.log(6 * (n - 0.85))) * self._concept_weights["Material"]

    def _support_equation(self, n) -> float:
        return (0.75 * (n / 1.5) ** .5) * self._concept_weights["Support"]

    def _mobility_equation(self, n) -> float:
        if 0 <= n <= 2:
            return (2 * ((n / 2) ** 2) * (3 - 2 * (n / 2))) * self._concept_weights["Mobility"]
        else:
            return (0.5 * math.sqrt(n - 1) + 1.5) * self._concept_weights["Mobility"]

    def _aggression_equation(self, n) -> float:
        return (0.35 * (n ** 0.5)) * self._concept_weights["Aggression"]

    def analyze(self, board: Board) -> float:
        total_eval: float = 0

        for sub_board_key in board.boards:
            sub_board: np.array = board.boards[sub_board_key]

            # Basic tracking of how many pieces are on a board (Material)
            piece_ratio: list[int] = [0, 0]

            piece_ratio[0] = np.sum(sub_board == Board.BLACK)
            piece_ratio[1] = np.sum(sub_board == Board.WHITE)

            if piece_ratio[0] == 0 or piece_ratio[1] == 0:
                return self.WHITE_WIN if piece_ratio[0] == 0 else self.BLACK_WIN

            # Tracking total amount of connections (Support, Aggression)
            support_connections: list[int] = [0, 0]
            aggressive_connections: list[int] = [0, 0]

            # Tracking mobility
            white_mobility: dict[tuple[int, int], float] = {}
            black_mobility: dict[tuple[int, int], float] = {}
            for direction in self._DIRECTIONS:
                white_mobility[direction] = 0.0
                black_mobility[direction] = 0.0

            # Scanning squares
            for x in range(4):
                for y in range(4):
                    # Getting piece and checking if square is emtpy
                    piece = sub_board[x][y]
                    if piece == Board.NONE:
                        continue

                    # Checking affiliations with directions and magnitudes (Aggression, Mobility, Support)
                    for dx_mag, dy_mag, dx, dy, mag in self._DIRECTION_MAG_OFFSETS:
                        x2, y2 = x + dx_mag, y + dy_mag

                        # Moving on if location is out of the sub board
                        if not Analyze._on_board(x2, y2):
                            continue

                        new_piece = sub_board[x2][y2]

                        # Checking for mobility
                        if new_piece == Board.NONE:
                            if piece == Board.BLACK:
                                black_mobility[(dx, dy)] += 0.5 if mag == 1 else 1

                            else:
                                white_mobility[(dx, dy)] += 0.5 if mag == 1 else 1

                        # Checking for support
                        if new_piece == piece:
                            support_connections[0 if piece == Board.BLACK else 1] += 1 if mag == 1 else 0.25

                        # Checking for aggression
                        if new_piece == - piece:
                            aggressive_connections[0 if piece == Board.BLACK else 1] += 1 if mag == 1 else 0.35

            # Calculating the weight of material
            total_eval += self._material_equation(piece_ratio[0]) - self._material_equation(piece_ratio[1])

            # Accounting for mobility
            for direction in self._DIRECTIONS:
                total_eval += self._mobility_equation(black_mobility[direction]) - self._mobility_equation(white_mobility[direction])

            # Accounting for Aggression
            total_eval += self._aggression_equation(aggressive_connections[0]) - self._aggression_equation(aggressive_connections[1])

            # Accounting for support
            total_eval += self._support_equation(support_connections[0]) - self._support_equation(support_connections[1])

        return total_eval
