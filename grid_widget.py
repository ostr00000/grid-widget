from __future__ import annotations

from typing import Set

from PyQt5.QtCore import QRect, QPoint, QSize
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QWidget, QSizePolicy

from nodes import PositionNode, ResourceNode
from visitor import countMaxColumns, rightBorderGen, filterType, balanceHorizontal, \
    balanceVertical, topDownLeftRightVisitor, countMaxRows


class GridGraph:

    def __init__(self, rect: QRect):
        self.balanced = True
        self._balanceCache = {}
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

    def insert(self, widget, rect: QRect):
        if len(self.resourceNodes) == 1 and self.resourceNodes[0].widget is None:
            self.resourceNodes[0].widget = widget
            return

        rightBorder = list(filterType(rightBorderGen(self.tr), PositionNode))
        tl = self.tr
        self.tr = PositionNode(rect.topRight())
        bl = self.br
        self.br = PositionNode(rect.bottomRight())

        rn = ResourceNode(self.tr, tl, bl, self.br, widget=widget)
        rn.left.extend(rightBorder[1:-1])
        self.resourceNodes.append(rn)

        for rb in rightBorder:
            rb.topRight = rn
            rb.bottomRight = rn

        rightBorder[0].topRight = None
        rightBorder[-1].bottomRight = None

        self.balance(rect)

    def balance(self, rect: QRect):
        columns = countMaxColumns(self.tl)
        maxColumn = columns[max(columns, key=columns.get)]
        widthFactor = int(rect.width() / maxColumn)
        balHor = balanceHorizontal(self.tl, maxColumn, columns)

        rows = countMaxRows(self.tl)
        maxRow = rows[max(rows, key=rows.get)]
        heightFactor = int(rect.height() / maxRow)
        balVer = balanceVertical(self.tl, maxRow, rows)

        globalBottomRight = rect.bottomRight() + QPoint(1, 1)
        visited: Set[int] = set()

        def updatePoint(posNode: PositionNode, y: int, x: int):
            posNodeId = id(posNode)
            if posNodeId not in visited:
                visited.add(posNodeId)

                q_point = QPoint(x, y)
                newPoint = globalBottomRight - q_point
                posNode.point = newPoint

        for node in topDownLeftRightVisitor(self.tl):
            nodeId = id(node)
            right = columns[nodeId] - 1
            left = right + balHor[nodeId]
            right *= widthFactor
            left *= widthFactor

            bottom = rows[nodeId] - 1
            top = bottom + balVer[nodeId]
            bottom *= heightFactor
            top *= heightFactor

            updatePoint(node.topRight, top, right)
            updatePoint(node.bottomRight, bottom, right)
            updatePoint(node.topLeft, top, left)
            updatePoint(node.bottomLeft, bottom, left)

            width = left - right
            height = top - bottom
            node.widget.move(node.topLeft.point)
            node.widget.resize(width, height)


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
