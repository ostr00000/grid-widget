import logging
import math
from dataclasses import dataclass, field
from operator import attrgetter
from typing import List, Tuple, Optional, Iterator

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLabel, QVBoxLayout


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

    def firstFreePosition(self, x: int, y: int) -> Optional[Position]:
        lastObject = self._data[x][y]
        if lastObject is None:
            return Position(x, y)
        elif len(lastObject.positions) > 1:
            return lastObject.bottomRight()

    def getLastPosition(self) -> Position:
        if self._data:
            x, y = self.x, self.y
            if pos := self.firstFreePosition(x, y):
                return pos

            elif x < y:
                self.incRow()
                return Position(0, y - 1)

            else:
                self.incCol()
                return Position(x - 1, 0)

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
        assert isinstance(item, QWidget)
        for row in self._data:
            for col in row:
                if col.widget == item:
                    return True
        return False


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = Grid()
        self.insertPosition = 0, 0

    def addWidget(self, widget: QWidget):
        assert widget not in self._grid
        pos = self._grid.getLastPosition()
        self._grid[pos] = GridObject([pos], widget)

        self.moveAll()
        widget.show()

    def moveAll(self):
        mySize = self.size()
        w, h = mySize.width(), mySize.height()

        rowFactor = w / self._grid.x
        colFactor = h / self._grid.y

        for gridObject in self._grid:
            topLeft = gridObject.topLeft()
            x = topLeft.x * rowFactor
            y = topLeft.y * colFactor

            bottomRight = gridObject.bottomRight()
            x2 = bottomRight.x * rowFactor
            y2 = bottomRight.y * colFactor

            gridObject.widget.resize(int(x2 - x), int(y2 - y))
            gridObject.widget.move(int(x), int(y))


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.num = 0

        self.button = QPushButton("Create widget")
        self.button.clicked.connect(self.onButtonClicked)
        self.verticalLayout.addWidget(self.button)

        self.gridWidget = GridWidget(self)
        self.verticalLayout.addWidget(self.gridWidget)

    def onButtonClicked(self):
        self.num += 1
        widget = QLabel(f"Label{self.num}", self)
        self.gridWidget.addWidget(widget)


def main():
    app = QApplication([])

    mmw = QMainWindow()
    mw = MyWidget(mmw)
    mmw.setCentralWidget(mw)
    mmw.show()

    app.exec()


if __name__ == '__main__':
    logging.basicConfig()
    main()
