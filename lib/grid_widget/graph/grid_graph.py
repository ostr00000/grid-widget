from typing import Set, List

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget

from grid_widget.graph.distributor import Distributor
from grid_widget.graph.nodes import PositionNode, ResourceNode
from grid_widget.graph.properties import GraphProperties
from grid_widget.graph.stretch import Stretcher
from grid_widget.graph.visitor import Filter, BorderGen, GraphVisitor


class GridGraph:

    def __init__(self, rect: QRect):
        self.resourceNodes: List[ResourceNode] = []
        self.positionNodes: List[PositionNode] = []

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

    def append(self, widget, rect: QRect):
        assert all(rn.widget != widget for rn in self.resourceNodes), "widget already added"
        if self._isEmpty():
            self.resourceNodes[0].widget = widget
            return

        if self.prop.maxColumnNumber > self.prop.maxRowNumber:
            self._appendBottom(widget, rect)
        else:
            self._appendRight(widget, rect)

        self.refreshPositions(rect)

    def refreshPositions(self, rect: QRect):
        dist = Distributor(self.tl)
        dist.distribute(rect)
        self.prop = dist.prop

    def _isEmpty(self):
        return len(self.resourceNodes) == 1 and self.resourceNodes[0].widget is None

    def _appendRight(self, widget: QWidget, rect: QRect):
        rightBorder = list(Filter.byType(
            BorderGen.topToDown(self.tr, walkRightSide=False), PositionNode))
        assert len(rightBorder) >= 2

        tl = self.tr
        self.tr = PositionNode(rect.topRight())
        bl = self.br
        self.br = PositionNode(rect.bottomRight())
        self.positionNodes.extend((self.tr, self.br))

        rn = ResourceNode(self.tr, tl, bl, self.br, widget=widget, left=rightBorder[1:-1])
        self.resourceNodes.append(rn)

        for rb in rightBorder:
            rb.topRight = rn
            rb.bottomRight = rn

        rightBorder[0].topRight = None
        rightBorder[-1].bottomRight = None

    def _appendBottom(self, widget: QWidget, rect: QRect):
        bottomBorder = list(Filter.byType(
            BorderGen.leftToRight(self.bl), PositionNode))
        assert len(bottomBorder) >= 2

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

    def remove(self, widget: QWidget):
        resourceNodes = [rn for rn in self.resourceNodes if rn.widget == widget]
        assert resourceNodes, "Widget does not belong to grid widget"
        assert len(resourceNodes) == 1, "found multiple resource nodes with same widget"
        resourceNode = resourceNodes[0]

        stretcher = Stretcher(resourceNode)
        stretcher.stretch()

        for posNode in resourceNode:
            if len(posNode) == 0:
                self.positionNodes.remove(posNode)

        self.resourceNodes.remove(resourceNode)
