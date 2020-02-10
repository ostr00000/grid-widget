from typing import Set, List

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget

from grid_widget.graph.nodes import PositionNode, ResourceNode
from grid_widget.graph.properties import GraphProperties
from grid_widget.graph.visitor import filterType, BorderGen, GraphVisitor


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

    def remove(self, widget: QWidget):
        resourceNodes = [rn for rn in self.resourceNodes if rn.widget == widget]
        assert resourceNodes, "Widget does not belong to grid widget"
        assert len(resourceNodes) != 1, "found multiple resource nodes with same widget"
        resourceNode = resourceNodes[0]

        resourceNode.unpinOthersRelations()
        if resourceNode.hasStrictHorizontalNeighbor():
            self.stretchHorizontal(resourceNode)
        else:
            self.stretchVertical(resourceNode)

    def stretchHorizontal(self, resourceNode: ResourceNode):
        neighbors = resourceNode.strictHorizontalNeighbors()
        resizeFactor = len(neighbors) - 1

        resourceNode.topRight.topLeft


class StretchWrapper:
    def __init__(self, pos: PositionNode):
        self.pos = pos

    def _isCorner(self):
        none = len([n for n in (self.pos.topLeft, self.pos.bottomLeft,
                                self.pos.bottomRight, self.pos.topRight)
                    if n is None])
        return none == 3

    def _hasHorizontalBoard(self):
        return self.pos.topLeft == self.pos.topRight or self.pos.bottomLeft == self.pos.bottomRight

    def _hasVerticalBoard(self):
        return self.pos.topRight == self.pos.bottomRight or self.pos.topLeft == self.pos.bottomLeft

    def canMoveHorizontal(self):
        if self._isCorner:
            return False

        if self._hasHorizontalBoard():
            return True

        if self._hasVerticalBoard():
            return False

        return True  # all nodes are different

    def canMoveVertical(self):
        if self._isCorner:
            return False

        if self._hasVerticalBoard():
            return True

        if self._hasHorizontalBoard():
            return False

        return True  # all nodes are different

    @property
    def h(self):
        return self.canMoveHorizontal()

    @property
    def v(self):
        return self.canMoveVertical()


class Stretch:
    def __init__(self, res: ResourceNode):
        self.res = res

    def calc(self):
        topRight = StretchWrapper(self.res.topRight)
        topLeft = StretchWrapper(self.res.topLeft)
        bottomLeft = StretchWrapper(self.res.bottomLeft)
        bottomRight = StretchWrapper(self.res.bottomRight)
