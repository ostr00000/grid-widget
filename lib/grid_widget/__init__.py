from __future__ import annotations

from typing import Tuple, Iterable

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from drag_widget.frame import DragFrame


class GridWidget(QWidget):
    def __init__(self, parent=None, createButtons=True):
        super().__init__(parent)
        self.mainLayout = QGridLayout(self)
        self.innerLayout = QGridLayout()

        if createButtons:
            self._createButtons()
            self.mainLayout.addWidget(self.addWidgetButton, 0, 0)
            self.mainLayout.addWidget(self.addRowButton, 1, 0)
            self.mainLayout.addWidget(self.removeRowButton, 2, 0)
            self.mainLayout.addWidget(self.addColumnButton, 0, 1)
            self.mainLayout.addWidget(self.removeColumnButton, 0, 2)

        self.mainLayout.addLayout(self.innerLayout, 1, 1, 2, 2)

    def _createButtons(self):
        self.addWidgetButton = QPushButton("Add empty widget")
        self.addWidgetButton.clicked.connect(self.addWidget)

        self.addRowButton = QPushButton("Add row")
        self.addRowButton.clicked.connect(self.onAddRow)
        self.removeRowButton = QPushButton("Remove row")
        self.removeRowButton.clicked.connect(
            lambda: self._removeWidgets(self._lastRowIndexGen()))

        self.addColumnButton = QPushButton("Add column")
        self.addColumnButton.clicked.connect(self.onAddColumn)
        self.removeColumnButton = QPushButton("Remove column")
        self.removeColumnButton.clicked.connect(
            lambda: self._removeWidgets(self._lastColIndexGen()))

    def sizeHint(self) -> QSize:
        return QSize(100, 100)

    @property
    def lastColumn(self):
        lastCol = self.innerLayout.columnCount() - 1
        while lastCol >= 0:
            for i in range(self.innerLayout.rowCount()):
                if self.innerLayout.itemAtPosition(i, lastCol):
                    return lastCol
            lastCol -= 1

        return -1

    @property
    def lastRow(self):
        lastR = self.innerLayout.rowCount() - 1
        while lastR >= 0:
            for i in range(self.innerLayout.columnCount()):
                if self.innerLayout.itemAtPosition(lastR, i):
                    return lastR
            lastR -= 1

        return -1

    def _lastColIndexGen(self):
        if (lastCol := self.lastColumn) >= 0:
            for i in range(self.innerLayout.rowCount()):
                yield i, lastCol

    def _lastRowIndexGen(self):
        if (lastRow := self.lastRow) >= 0:
            for i in range(self.innerLayout.columnCount()):
                yield lastRow, i

    def _removeWidgets(self, positions: Iterable[Tuple[int, int]]):
        for row, col in positions:
            if item := self.innerLayout.itemAtPosition(row, col):
                self.innerLayout.removeItem(item)
                if widget := item.widget():
                    # noinspection PyTypeChecker
                    widget.setParent(None)

    def onAddRow(self):
        self.innerLayout.addWidget(DragFrame(self), self.lastRow + 1, 0)

    def onAddColumn(self):
        self.innerLayout.addWidget(DragFrame(self), 0, self.lastColumn + 1)

    def addWidget(self, widget: QWidget = None):
        if not isinstance(widget, QWidget):
            widget = DragFrame()
        self.innerLayout.addWidget(widget, *self._getFreePosition())
        widget.show()

    def _getFreePosition(self) -> Tuple[int, int]:
        rc = self.lastRow + 1
        cc = self.lastColumn + 1

        for x in range(rc):
            for y in range(cc):
                if self.innerLayout.itemAtPosition(x, y) is None:
                    return x, y

        if rc <= cc:
            return rc, 0
        else:
            return 0, cc
