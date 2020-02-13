from typing import TypeVar, Tuple, Callable, Iterable, List

from PyQt5.QtCore import QRect
from boltons.cacheutils import cachedproperty

from grid_widget import Distributor
from grid_widget.graph.nodes import ResourceNode, PositionNode, PositionContainer
from grid_widget.graph.visitor import Filter, GraphVisitor, BorderGen

TPN = Tuple[PositionNode, ...]


class PositionNodeProperties:
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
        if self._isCorner():
            return False

        if self._hasHorizontalBoard():
            return True

        if self._hasVerticalBoard():
            return False

        return True  # all nodes are different

    def canMoveVertical(self):
        if self._isCorner():
            return False

        if self._hasVerticalBoard():
            return True

        if self._hasHorizontalBoard():
            return False

        return True  # all nodes are different

    @cachedproperty
    def h(self):
        return self.canMoveHorizontal()

    @cachedproperty
    def v(self):
        return self.canMoveVertical()


class Stretcher:
    def __init__(self, remNode: ResourceNode):
        self.remNode = remNode
        self.newCorners = PositionContainer.fromPositionContainer(remNode)
        self.nodesToResize = []

    def stretch(self):
        topRight = PositionNodeProperties(self.remNode.topRight)
        topLeft = PositionNodeProperties(self.remNode.topLeft)
        bottomLeft = PositionNodeProperties(self.remNode.bottomLeft)
        bottomRight = PositionNodeProperties(self.remNode.bottomRight)

        if topRight.h and topLeft.h and bottomLeft.h and bottomRight.h:
            leftTop, leftBottom = self.getLeftNodes()
            rightTop, rightBottom = self.getRightNodes()
            totalRect = QRect(self.newCorners.topLeft.point, self.newCorners.bottomRight.point)

        elif topRight.v and topLeft.v and bottomLeft.v and bottomRight.v:
            raise NotImplementedError

        elif topRight.h and bottomRight.h:
            raise NotImplementedError

        elif topLeft.h and bottomLeft.h:
            leftTop, leftBottom = self.getLeftNodes()
            totalRect = QRect(self.newCorners.topLeft.point, self.remNode.bottomRight.point)
            self.newCorners.topRight = self.remNode.topLeft
            self.newCorners.bottomRight = self.remNode.bottomLeft

        elif topRight.v and topLeft.v:
            raise NotImplementedError

        elif bottomRight.v and bottomLeft.v:
            raise NotImplementedError

        else:  # is it possible? yes
            # leave resource node without widget
            raise NotImplementedError

        self.remNode.unpinOthersRelations()
        Distributor(self.newCorners, filterNodes=self.nodesToResize).distribute(totalRect)

    def getLeftNodes(self):
        leftTopPoints = list(Filter.byPosY(
            BorderGen.rightToLeft(self.remNode.topLeft, walkTopSide=False),
            self.remNode.topLeft.point.y()))
        leftBottomPoints = list(Filter.byPosY(
            BorderGen.rightToLeft(self.remNode.bottomLeft, walkTopSide=True),
            self.remNode.bottomLeft.point.y()))

        gen = commonValuesGen(leftTopPoints, leftBottomPoints, lambda x, y: -cmpX(x, y))
        commonLeftTopPoints, commonLeftBottomPoints = list(zip(*gen))  # type: TPN, TPN
        lTop, lBot = commonLeftTopPoints[-1], commonLeftBottomPoints[-1]

        nodesToResize = list(Filter.byRect(
            GraphVisitor.topDownLeftRightVisitor(lTop),
            QRect(lTop.point, self.remNode.bottomLeft.point)))
        self.nodesToResize.extend(nodesToResize)

        self.newCorners.topLeft = lTop
        self.newCorners.bottomLeft = lBot

    def getRightNodes(self):
        rightTopPoints = list(Filter.byPosY(
            BorderGen.leftToRight(self.remNode.topRight, walkTopSide=False),
            self.remNode.topLeft.point.y()))
        rightBottomPoints = list(Filter.byPosY(
            BorderGen.leftToRight(self.remNode.bottomRight, walkTopSide=True),
            self.remNode.bottomLeft.point.y()))

        gen = commonValuesGen(rightTopPoints, rightBottomPoints, cmpX)
        commonRightTopPoints, commonRightBottomPoints = list(zip(*gen))  # type: TPN, TPN
        rTop, rBot = commonRightTopPoints[-1], commonRightBottomPoints[-1]

        nodeToResize = list(Filter.byRect(
            GraphVisitor.topDownLeftRightVisitor(rTop),
            QRect(rTop.point, self.remNode.bottomRight.point)))
        self.nodesToResize.extend(nodeToResize)

        self.newCorners.topRight = rTop
        self.newCorners.bottomLeft = rBot


def cmpX(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.x() - pn2.point.x()


def cmpY(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.y() - pn2.point.y()


T = TypeVar('T')


def commonValuesGen(a: Iterable[T], b: Iterable[T],
                    cmpFun: Callable[[T, T], int]) -> Iterable[Tuple[T, T]]:
    a = iter(a)
    b = iter(b)
    longestA = next(a)
    longestB = next(b)
    assert 0 == cmpFun(longestA, longestB), "First pair must be equal"
    yield longestA, longestB

    try:
        while True:
            nextA = next(a)
            nextB = next(b)
            while (c := cmpFun(nextA, nextB)) != 0:
                if c < 0:
                    nextA = next(a)
                else:
                    nextB = next(b)
            longestA, longestB = nextA, nextB
            yield longestA, longestB

    except StopIteration:
        pass
