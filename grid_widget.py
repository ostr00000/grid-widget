from __future__ import annotations

from typing import Set

from PyQt5.QtCore import QRect, QPoint, QSize
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget, QSizePolicy

from graph_properties import GraphProperties
from nodes import PositionNode, ResourceNode
from visitor import filterType, BorderGen, GraphVisitor


class GridGraph:

    def __init__(self, rect: QRect):
        self.resourceNodes = []
        self.positionNodes = []

        self.tr = PositionNode(rect.topRight())
        self.tl = PositionNode(rect.topLeft())
        self.bl = PositionNode(rect.bottomLeft())
        self.br = PositionNode(rect.bottomRight())

        rn = ResourceNode(self.tr, self.tl, self.bl, self.br)
        self.tr.bottomLeft = rn
        self.tl.bottomRight = rn
        self.bl.topRight = rn
        self.br.topLeft = rn

        self.resourceNodes.append(rn)
        self.positionNodes.extend([self.tr, self.tl, self.bl, self.br])
        self.prop = GraphProperties(self.tl)

    def insert(self, widget, rect: QRect):
        if self._isEmpty():
            self.resourceNodes[0].widget = widget
            return

        if self.prop.maxColumnNumber > self.prop.maxRowNumber:
            self._appendBottom(widget, rect)
        else:
            self._appendRight(widget, rect)

        self.balance(rect)

    def _isEmpty(self):
        return len(self.resourceNodes) == 1 and self.resourceNodes[0].widget is None

    def _appendRight(self, widget: QWidget, rect: QRect):
        rightBorder = list(filterType(BorderGen.right(self.tr), PositionNode))
        tl = self.tr
        self.tr = PositionNode(rect.topRight())
        bl = self.br
        self.br = PositionNode(rect.bottomRight())

        rn = ResourceNode(self.tr, tl, bl, self.br, widget=widget, left=rightBorder[1:-1])
        self.resourceNodes.append(rn)

        for rb in rightBorder:
            rb.topRight = rn
            rb.bottomRight = rn

        rightBorder[0].topRight = None
        rightBorder[-1].bottomRight = None

    def _appendBottom(self, widget: QWidget, rect: QRect):
        bottomBorder = list(filterType(BorderGen.bottom(self.bl), PositionNode))
        tr = self.br
        tl = self.bl
        self.bl = PositionNode(rect.bottomLeft())
        self.br = PositionNode(rect.bottomRight())

        rn = ResourceNode(tr, tl, self.bl, self.br, widget=widget, top=bottomBorder[1:-1])
        self.resourceNodes.append(rn)

        for rb in bottomBorder:
            rb.bottomLeft = rn
            rb.bottomRight = rn

        bottomBorder[0].bottomLeft = None
        bottomBorder[-1].bottomRight = None

    def balance(self, rect: QRect):
        self.prop = GraphProperties(self.tl)

        widthFactor = int(rect.width() / self.prop.maxColumnNumber)
        heightFactor = int(rect.height() / self.prop.maxRowNumber)
        globalBottomRight = rect.bottomRight() + QPoint(1, 1)
        visited: Set[int] = set()

        def updatePoint(posNode: PositionNode, y: int, x: int):
            posNodeId = id(posNode)
            if posNodeId not in visited:
                visited.add(posNodeId)

                q_point = QPoint(x, y)
                newPoint = globalBottomRight - q_point
                posNode.point = newPoint

        for node in GraphVisitor.topDownLeftRightVisitor(self.tl):
            nodeId = id(node)
            right = self.prop.node2ColumnNumber[nodeId] - 1
            left = right + self.prop.node2horizontalSize[nodeId]
            right *= widthFactor
            left *= widthFactor

            bottom = self.prop.node2RowNumber[nodeId] - 1
            top = bottom + self.prop.node2VerticalSize[nodeId]
            bottom *= heightFactor
            top *= heightFactor

            updatePoint(node.topRight, top, right)
            updatePoint(node.bottomRight, bottom, right)
            updatePoint(node.topLeft, top, left)
            updatePoint(node.bottomLeft, bottom, left)

            node.updateWidget()


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = GridGraph(self.rect())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(800, 800)

    def addWidget(self, widget: QWidget):
        widget.setParent(self)
        self._grid.insert(widget, self.rect())
        widget.show()

    def paintEvent(self, event: QPaintEvent) -> None:
        self._grid.balance(self.rect())
