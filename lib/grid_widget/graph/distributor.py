from typing import Set, List

from PyQt5.QtCore import QRect, QPoint

from grid_widget.graph.nodes import PositionNode, ResourceNode
from grid_widget.graph.properties import GraphProperties
from grid_widget.graph.visitor import GraphVisitor


class Distributor:
    def __init__(self, topLeft: PositionNode, filterNodes: List[ResourceNode] = None):
        self.topLeft = topLeft
        self.prop = GraphProperties(self.topLeft, filterNodes=filterNodes)

    def distribute(self, rect: QRect):
        widthFactor = int(rect.width() / self.prop.maxColumnNumber)
        heightFactor = int(rect.height() / self.prop.maxRowNumber)
        globalBottomRight = rect.bottomRight() + QPoint(1, 1)  # TODO maybe better not add
        visited: Set[int] = set()

        def updatePoint(posNode: PositionNode, y: int, x: int):
            posNodeId = id(posNode)
            if posNodeId not in visited:
                visited.add(posNodeId)

                q_point = QPoint(x, y)
                newPoint = globalBottomRight - q_point
                posNode.point = newPoint

        for node in GraphVisitor.topDownLeftRightVisitor(self.topLeft):
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
