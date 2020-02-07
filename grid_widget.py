from dataclasses import dataclass, field
from operator import attrgetter
from typing import Optional, List, Union, Type, TypeVar, Iterable, Dict

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QWidget


@dataclass
class Node:
    pass


@dataclass
class PositionNode(Node):
    point: QPoint

    topRight: Optional['ResourceNode'] = None
    topLeft: Optional['ResourceNode'] = None
    bottomLeft: Optional['ResourceNode'] = None
    bottomRight: Optional['ResourceNode'] = None


@dataclass
class ResourceNode:
    topRight: PositionNode
    topLeft: PositionNode
    bottomLeft: PositionNode
    bottomRight: PositionNode

    widget: Optional[QWidget] = None

    top: List[PositionNode] = field(default_factory=list)
    left: List[PositionNode] = field(default_factory=list)
    bottom: List[PositionNode] = field(default_factory=list)
    right: List[PositionNode] = field(default_factory=list)

    def rightPositionsGen(self) -> Iterable['ResourceNode']:
        rightBorder = [self.topRight] + self.right + [self.bottomRight]
        for posNode in rightBorder:
            if n := posNode.topRight:
                yield n
            if n := posNode.bottomRight:
                yield n


NodeType = TypeVar('NodeType', ResourceNode, PositionNode)


def _filterGen(iterable, *types):
    for i in iterable:
        if isinstance(i, types):
            yield i


def _nodeGen(topPositionNode: PositionNode, isRightBorder: bool) -> NodeType:
    nextRes = attrgetter('bottomRight' if isRightBorder else 'bottomLeft')
    nextPos = attrgetter('bottomLeft' if isRightBorder else 'bottomRight')

    yield topPositionNode
    while resourceNode := nextRes(topPositionNode):
        yield resourceNode
        topPositionNode = nextPos(resourceNode)
        yield topPositionNode


@dataclass
class BalanceCache:
    initialGuess: int
    correction: int


class GraphTravel:
    def __init__(self, gridGraph):
        self.gridGraph: GridGraph = gridGraph
        self._maxValCache = {}
        self._balanceCache: Dict[int, BalanceCache] = {}

    def leftBorderNodeGen(self, *allowNode: Type[NodeType]) -> Iterable[NodeType]:
        yield from _filterGen(_nodeGen(self.gridGraph.tl, True), allowNode)

    def rightBorderNodeGen(self, *allowNode: Union[Type[ResourceNode], Type[PositionNode]]):
        yield from _filterGen(_nodeGen(self.gridGraph.tr, False), allowNode)

    def countMaxColumns(self):
        """Take maximum value from nodes on left"""
        maxVal = 0
        self._maxValCache.clear()

        for resourceNode in self.leftBorderNodeGen(ResourceNode):
            maxVal = max(self._countMaxColumns(resourceNode), maxVal)

        return maxVal

    def _countMaxColumns(self, resNode: ResourceNode) -> int:
        """Ask each right node 'How many nodes are on the right?',
         take maximum value and add self"""
        try:
            maxVal = self._maxValCache[id(resNode)]
        except KeyError:
            maxVal = max((self._countMaxColumns(rn) for rn in resNode.rightPositionsGen()),
                         default=0) + 1
            self._maxValCache[id(resNode)] = maxVal
        return maxVal

    def balance(self, rect: QRect):
        columns = self.countMaxColumns()
        if not columns:
            return
        avg = int(rect.width() / columns)

        for resourceNode in self.leftBorderNodeGen(ResourceNode):
            self._balance(resourceNode, columns)

    def _balance(self, resourceNode: ResourceNode, columns: int):
        """
        1. let right node prepare
        2. calc diff with child and correct its value
        3. set own value
        """
        if id(resourceNode) in self._balanceCache:
            return

        myMaxCount = self._countMaxColumns(resourceNode)

        for rn in resourceNode.rightPositionsGen():
            self._balance(rn, columns)
            diff = myMaxCount - self._countMaxColumns(rn)
            self._balanceCache[id(rn)].correction = diff

        myColumns = columns - myMaxCount + 1
        self._balanceCache[id(resourceNode)] = BalanceCache(myColumns, myColumns)


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

        rightBorder = [rn for rn in GraphTravel(self).rightBorderNodeGen(PositionNode)]
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

        GraphTravel(self).balance(rect)


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = GridGraph(self.rect())

    def addWidget(self, widget: QWidget):
        widget.setParent(self)
        self._grid.insert(widget, self.rect())
        widget.show()
