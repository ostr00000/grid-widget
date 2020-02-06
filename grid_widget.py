from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget

from grid import Grid, GridObject


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = Grid()
        self.insertPosition = 0, 0

    def addWidget(self, widget: QWidget):
        assert widget not in self._grid
        widget.setParent(self)

        pos = self._grid.getLastPosition()
        self._grid[pos] = GridObject([pos], widget)

        self.update()
        widget.show()

    def paintEvent(self, paintEvent: QPaintEvent = None) -> None:
        if not self._grid:
            return
        mySize = self.size()
        w, h = mySize.width(), mySize.height()

        rowFactor = w / self._grid.x
        colFactor = h / self._grid.y

        for gridObject in self._grid:
            topLeft = gridObject.topLeft()
            x = topLeft.x * rowFactor
            y = topLeft.y * colFactor

            bottomRight = gridObject.bottomRight()
            x2 = (bottomRight.x + 1) * rowFactor
            y2 = (bottomRight.y + 1) * colFactor

            gridObject.widget.resize(int(x2 - x), int(y2 - y))
            gridObject.widget.move(int(x), int(y))
