class Cord:
    _BOUNDS = [0, 1, 2, 3]

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def readable_x(self) -> int:
        return self._x + 1

    @property
    def readable_y(self) -> int:
        return self._y + 1

    @property
    def valid(self) -> bool:
        return self._x in self._BOUNDS and self._y in self._BOUNDS

    def __add__(self, other):
        return Cord(self._x + other.x, self._y + other.y)

    def __sub__(self, other):
        return Cord(self._x - other.x, self._y - other.y)

    def __mul__(self, other):
        return Cord(self._x * other, self._y * other)

    def __str__(self):
        return f"[{self._x}, {self._y}]"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Move:
    def __init__(self, start: Cord, end: Cord):
        self._start: Cord = start
        self._end: Cord = end

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def valid(self) -> bool:
        return self._start.valid and self._end.valid

    @property
    def difference(self) -> Cord:
        return Cord(self._end.x - self._start.x, self._end.y - self._start.y)

    @property
    def normalized_difference(self) -> Cord:
        dx = self.difference.x
        dy = self.difference.y

        # Calculate normalized values based on maximum absolute component
        max_component = max(abs(dx), abs(dy))

        if max_component == 0:
            return Cord(0, 0)

        return Cord(
            int(dx / max_component),
            int(dy / max_component)
        )

    @property
    def magnitude(self):
        return max(abs(self.difference.x), abs(self.difference.y))

    def __add__(self, other):
        return Move(self._start + other.start, self._end + other.end)

    def __sub__(self, other):
        return Move(self._start - other.start, self._end - other.end)

    def __mul__(self, other):
        return Move(self._start * other, self._end * other)

    def __str__(self):
        return f"{self._start} => {self._end}"

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end


class MovePair:
    def __init__(self, passive_move: Move, aggressive_move: Move, passive_board: str, aggressive_board: str):
        self._passive_move: Move = passive_move
        self._aggressive_move: Move = aggressive_move

        self._passive_board: str = passive_board
        self._aggressive_board: str = aggressive_board

    @property
    def passive_move(self) -> Move:
        return self._passive_move

    @property
    def aggressive_move(self) -> Move:
        return self._aggressive_move

    @property
    def passive_board(self) -> str:
        return self._passive_board

    @property
    def aggressive_board(self) -> str:
        return self._aggressive_board

    def __str__(self):
        return f"Passive    ({self._passive_board}): {self._passive_move}\nAggressive ({self._aggressive_board}): {self._aggressive_move}"

    def __eq__(self, other):
        return self.passive_move == other.passive_move and self.aggressive_move == other.aggressive_move and self.passive_board == other.passive_board and self.aggressive_board == other.aggressive_board
