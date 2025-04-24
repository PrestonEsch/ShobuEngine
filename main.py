from app import run_gui

from shobu import Board

from app.engine import Analyze, Engine

import time


def test_function_speed(func, trials: int):
    start_time = time.time_ns()

    for _ in range(trials):
        func()

    return time.time_ns() - start_time


if __name__ == '__main__':
    run_gui()
    # e = Engine()
    # b = Board()
    #
    # c = e.get_best_move(b, 2, threads=24)
    # b.make_move(c)
    #
    # d = e.get_best_move(b, 3, threads=24)
    # b.make_move(d)
    #
    # f = e.get_best_move(b, 2, threads=24)
    # b.make_move(f)
    #
    # g = e.get_best_move(b, 3, threads=24)
    # b.make_move(g)
    #
    # print(c)
    # print(d)
