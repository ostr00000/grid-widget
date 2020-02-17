from __future__ import annotations

from typing import Tuple

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._gridLayout = QGridLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(100, 100)

    def addWidget(self, widget: QWidget):
        widget.setParent(self)
        self._gridLayout.addWidget(widget, *self._getFreePosition())
        widget.show()

    def _getFreePosition(self) -> Tuple[int, int]:
        rc = self._gridLayout.rowCount()
        cc = self._gridLayout.columnCount()

        for x in range(rc):
            for y in range(cc):
                if self._gridLayout.itemAtPosition(x, y) is None:
                    return x, y

        if rc <= cc:
            return rc, 0
        else:
            return 0, cc
