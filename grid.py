import math
from dataclasses import dataclass, field
from typing import List, Optional, Iterator, Tuple

from PyQt5.QtWidgets import QWidget


def getArraySize(num: int) -> Tuple[int, int]:
    a = int(math.sqrt(num))
    if a * a == num:
        return a, a

    elif a * (a + 1) == num:
        return a, a + 1


@dataclass
class Position:
    x: int
    y: int


@dataclass
class GridObject:
    positions: List[Position] = field(default_factory=list)
    widget: Optional[QWidget] = None

    def __eq__(self, other):
        return isinstance(other, GridObject) and self.widget == other.widget

    def __hash__(self):
        return hash(id(self.widget))

    def topLeft(self) -> Position:
        return min(self.positions, key=lambda pos: (pos.x, pos.y))

    def topRight(self) -> Position:
        return min(self.positions, key=lambda pos: (pos.x, -pos.y))

    def bottomLeft(self) -> Position:
        return min(self.positions, key=lambda pos: (-pos.x, pos.y))

    def bottomRight(self) -> Position:
        return min(self.positions, key=lambda pos: (-pos.x, -pos.y))


class Grid:
    def __init__(self):
        self._data: List[List[Optional[GridObject]]] = []

    @property
    def x(self):
        return len(self._data)

    @property
    def y(self):
        return len(self._data[0]) if self._data else 0

    def incRow(self):
        self._data.append([None] * self.y)

    def incCol(self):
        for row in self._data:
            row.append(None)

    def __getitem__(self, item):
        assert isinstance(item, Position)
        assert item.x < self.x
        assert item.y < self.y
        return self._data[item.x][item.y]

    def __setitem__(self, key, value):
        assert isinstance(key, Position)
        assert isinstance(value, GridObject)
        assert key.x < self.x
        assert key.y < self.y
        curObj = self._data[key.x][key.y]
        if curObj:
            assert len(curObj.positions) > 1
        self._data[key.x][key.y] = value

    def getLastPosition(self) -> Position:
        if self._data:
            x, y = self.x, self.y

            if self._data[x - 1][y - 1] is None:
                return Position(x, y)

            elif x < y:
                self.incRow()
                return Position(x, 0)

            else:
                self.incCol()
                return Position(0, y)

        else:
            self.incRow()
            self.incCol()
            return Position(0, 0)

    def __iter__(self) -> Iterator[GridObject]:
        allObjects = set()
        for row in self._data:
            for col in row:
                allObjects.add(col)

        return iter(allObjects)

    def __contains__(self, item):
        if isinstance(item, QWidget):
            for row in self._data:
                for col in row:
                    if col.widget == item:
                        return True
        return False

    def __bool__(self):
        return len(self._data) != 0
