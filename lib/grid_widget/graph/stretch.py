from typing import TypeVar, Tuple, Callable, Iterable, Optional, List

from PyQt5.QtCore import QRect
from boltons.cacheutils import cachedproperty

from grid_widget import Distributor
from grid_widget.graph.nodes import ResourceNode, PositionNode, PositionContainer
from grid_widget.graph.visitor import Filter, GraphVisitor, BorderGen


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
    def __init__(self, res: ResourceNode):
        """
        :param res: Removed node
        """
        self.res = res
        self.newCorners = PositionContainer.fromPositionContainer(res)

    def stretch(self):
        topRight = PositionNodeProperties(self.res.topRight)
        topLeft = PositionNodeProperties(self.res.topLeft)
        bottomLeft = PositionNodeProperties(self.res.bottomLeft)
        bottomRight = PositionNodeProperties(self.res.bottomRight)

        nodesToResize = []
        if topRight.h and topLeft.h and bottomLeft.h and bottomRight.h:
            nodesToResize.extend(self.getLeftNodes())
            raise NotImplementedError
        elif topRight.v and topLeft.v and bottomLeft.v and bottomRight.v:
            raise NotImplementedError

        elif topRight.h and bottomRight.h:
            raise NotImplementedError
        elif topLeft.h and bottomLeft.h:
            nodesToResize.extend(self.getLeftNodes())
            totalRect = QRect(self.newCorners.topLeft.point, self.res.bottomRight.point)
            self.newCorners.topRight = self.res.topLeft
            self.newCorners.bottomRight = self.res.bottomLeft
        elif topRight.v and topLeft.v:
            raise NotImplementedError
        elif bottomRight.v and bottomLeft.v:
            raise NotImplementedError

        else:  # is it possible? yes
            # leave resource node without widget
            raise NotImplementedError

        self.res.unpinOthersRelations()
        Distributor(self.newCorners, filterNodes=nodesToResize).distribute(totalRect)

    def getLeftNodes(self) -> List[ResourceNode]:
        leftTopPoints = list(Filter.byPosY(
            BorderGen.rightToLeft(self.res.topLeft), self.res.topLeft.point.y()))
        leftBottomPoints = list(Filter.byPosY(
            BorderGen.rightToLeft(self.res.bottomLeft, walkTopSide=True),
            self.res.bottomLeft.point.y()))
        lTop, lBot = longestCommonValues(
            leftTopPoints, leftBottomPoints, lambda x, y: -cmpX(x, y))

        toResize = list(Filter.byRect(
            GraphVisitor.topDownLeftRightVisitor(lTop),
            QRect(lTop.point, self.res.bottomLeft.point)))

        self.newCorners.topLeft = lTop
        self.newCorners.bottomLeft = lBot

        return toResize


def cmpX(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.x() - pn2.point.x()


def cmpY(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.y() - pn2.point.y()


T = TypeVar('T')


def longestCommonValues(a: Iterable[T], b: Iterable[T],
                        cmpFun: Callable[[T, T], int]) -> Tuple[T, T]:
    a = iter(a)
    b = iter(b)
    longestA = next(a)
    longestB = next(b)
    assert 0 == cmpFun(longestA, longestB), "First pair must be equal"

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

    except StopIteration:
        return longestA, longestB
