from __future__ import annotations

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget, QSizePolicy

from grid_widget.graph.distributor import Distributor
from grid_widget.graph.grid_graph import GridGraph


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = GridGraph(self.rect())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(800, 800)

    def addWidget(self, widget: QWidget):
        widget.setParent(self)
        self._grid.append(widget, self.rect())
        widget.show()

    def removeWidget(self, widget: QWidget):
        self._grid.remove(widget)
        widget.setParent(None)

    def paintEvent(self, event: QPaintEvent) -> None:
        Distributor(self._grid.tl).distribute(self.rect())
