from concurrent.futures import ThreadPoolExecutor, as_completed

from shobu import Board

from .analyze import Analyze
from .board_node import BoardNode


class Engine:
    def __init__(self):
        self._analysis_cache: dict[str, float] = {}

        self._analysis = Analyze(None)

    def analyze(self, board: Board):
        if board.serialized_string not in self._analysis_cache:
            self._analysis_cache[board.serialized_string] = self._analysis.analyze(board)

        return self._analysis_cache[board.serialized_string]

    def _minimax(self, current_board: Board, current_depth: int, alpha, beta):
        if current_board.has_winner() or current_depth == 0:
            return self.analyze(current_board), current_board

        if current_board.current_player_turn == Board.BLACK:
            max_eval = float('-inf')
            selected_move = None

            for move in current_board.get_legal_moves():
                child_board = current_board.get_mock(move, keep_metadata=True, keep_moves=True)

                child_eval, _ = self._minimax(child_board, current_depth - 1, alpha, beta)

                if child_eval > max_eval:
                    max_eval = child_eval
                    selected_move = move

                alpha = max(alpha, child_eval)
                if beta >= alpha:
                    break

            return max_eval, selected_move

        elif current_board.current_player_turn == Board.WHITE:
            min_eval = float('inf')
            selected_move = None

            for move in current_board.get_legal_moves():
                child_board = current_board.get_mock(move, keep_metadata=True, keep_moves=True)

                child_eval, _ = self._minimax(child_board, current_depth - 1, alpha, beta)

                if child_eval < min_eval:
                    min_eval = child_eval
                    selected_move = move

                beta = min(beta, child_eval)
                if beta <= alpha:
                    break

            return min_eval, selected_move

    def get_best_move(self, board: Board, depth: int, threads: int = 1):
        def score_move(move):
            child_board = board.get_mock(move, keep_metadata=True, keep_moves=True)

            return self._minimax(child_board, depth - 1, alpha, beta)[0], move

        legal_moves = board.get_legal_moves()
        legal_moves.sort(key=lambda m: self.analyze(board.get_mock(m)), reverse=board.current_player_turn == Board.BLACK)

        is_maximizing = board.current_player_turn == Board.BLACK

        alpha, beta = float('-inf'), float('inf')

        best_score = float('-inf') if is_maximizing else float('inf')
        best_move = None

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(score_move, move): move for move in legal_moves}

            for future in as_completed(futures):
                score, move = future.result()

                if is_maximizing and score > best_score:
                    best_score = score
                    best_move = move
                elif not is_maximizing and score < best_score:
                    best_score = score
                    best_move = move

        return best_move, best_score
