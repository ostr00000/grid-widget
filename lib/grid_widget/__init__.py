from __future__ import annotations

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget, QSizePolicy

from grid_widget.graph.distributor import Distributor
from grid_widget.graph.grid_graph import GridGraph

import logging

logger = logging.getLogger(__name__)


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = GridGraph(self.rect())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def renderGraph(self):
        try:
            dot = self._grid.dump()
        except ImportError:
            return

        dot.engine = 'neato'
        outFile = dot.render(
            'graph_widget', directory='out', format='png', cleanup=True)
        logger.info(outFile)

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
        self._grid.refreshPositions(self.rect())
        self.renderGraph()
