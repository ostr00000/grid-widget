import functools
import operator
from typing import Set, List

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget

from grid_widget.graph.distributor import Distributor
from grid_widget.graph.nodes import PositionNode, ResourceNode, PositionContainer
from grid_widget.graph.properties import GraphProperties
from grid_widget.graph.stretch import Stretcher
from grid_widget.graph.visitor import Filter, BorderGen, GraphVisitor


class GridGraph:

    def dump(self):
        from graphviz import Digraph
        dot = Digraph()

        for pn in self.positionNodes:
            dot.node(str(id(pn)), label=str(pn), pos=f'{pn.point.x()},{-pn.point.y()}')

        for rn in self.resourceNodes:
            p = functools.reduce(operator.add, (pn.point for pn in rn), QPoint())
            p /= 4
            dot.node(str(id(rn)), label=str(rn), pos=f'{p.x()},{-p.y()}')

            for pn in rn:
                dot.edge(str(id(rn)), str(id(pn)))

        return dot

    def __init__(self, rect: QRect):
        self.positionNodes: List[PositionNode] = []
        self.corner = PositionContainer.fromRect(rect)
        self.positionNodes.extend(self.corner)

        self.resourceNodes: List[ResourceNode] = []
        rn = ResourceNode.fromPositionContainer(self.corner)
        self.resourceNodes.append(rn)

        self.prop = GraphProperties(self.corner)

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

    def refreshPositions(self, rect: QRect = None):
        if rect is None:
            rect = QRect(self.corner.topLeft.point, self.corner.bottomRight.point)
        dist = Distributor(self.corner)
        dist.distribute(rect)
        self.prop = dist.prop

    def _isEmpty(self):
        return len(self.resourceNodes) == 1 and self.resourceNodes[0].widget is None

    def _appendRight(self, widget: QWidget, rect: QRect):
        rightBorder = list(Filter.byType(
            BorderGen.topToDown(self.corner.topRight, walkRightSide=False),
            PositionNode))
        assert len(rightBorder) >= 2

        tl = self.corner.topRight
        bl = self.corner.bottomRight

        self.corner.topRight = tr = PositionNode(rect.topRight())
        self.corner.bottomRight = br = PositionNode(rect.bottomRight())
        self.positionNodes.extend((tr, br))

        rn = ResourceNode(tr, tl, bl, br, widget=widget, left=rightBorder[1:-1])
        self.resourceNodes.append(rn)

        for rb in rightBorder:
            rb.topRight = rn
            rb.bottomRight = rn

        rightBorder[0].topRight = None
        rightBorder[-1].bottomRight = None

    def _appendBottom(self, widget: QWidget, rect: QRect):
        bottomBorder = list(Filter.byType(
            BorderGen.leftToRight(self.corner.bottomLeft), PositionNode))
        assert len(bottomBorder) >= 2

        tr = self.corner.bottomRight
        tl = self.corner.bottomLeft

        self.corner.bottomLeft = bl = PositionNode(rect.bottomLeft())
        self.corner.bottomRight = br = PositionNode(rect.bottomRight())
        self.positionNodes.extend((bl, br))

        rn = ResourceNode(tr, tl, bl, br, widget=widget, top=bottomBorder[1:-1])
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

        it = zip(resourceNode, stretcher.newCorners)
        for posNode, newPosNode in it:  # type: PositionNode, PositionContainer
            if len(posNode) == 0:
                self.corner.update(posNode, newPosNode)
                self.positionNodes.remove(posNode)

        self.resourceNodes.remove(resourceNode)
        self.refreshPositions()
