from typing import TypeVar, Tuple, Callable, Iterator

from boltons.cacheutils import cachedproperty

from grid_widget.graph.nodes import ResourceNode, PositionNode
from grid_widget.graph.visitor import StrictLineGen, filterType, GraphVisitor


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

    def stretch(self):
        topRight = PositionNodeProperties(self.res.topRight)
        topLeft = PositionNodeProperties(self.res.topLeft)
        bottomLeft = PositionNodeProperties(self.res.bottomLeft)
        bottomRight = PositionNodeProperties(self.res.bottomRight)

        if topRight.h and topLeft.h and bottomLeft.h and bottomRight.h:
            self.horizontal(left=True, right=True)
        elif topRight.v and topLeft.v and bottomLeft.v and bottomRight.v:
            self.vertical(top=True, bottom=True)

        elif topRight.h and bottomRight.h:
            self.horizontal(right=True)
        elif topLeft.h and bottomRight.h:
            self.horizontal(left=True)
        elif topRight.v and topLeft.v:
            self.vertical(top=True)
        elif bottomRight.v and bottomLeft.v:
            self.vertical(bottom=True)

    def horizontal(self, left=False, right=False):
        if left:
            leftTopPoints = [self.res.topLeft] + list(filterType(
                StrictLineGen.rightToLeft(self.res.topLeft),
                PositionNode))
            leftBottomPoints = [self.res.bottomLeft] + list(filterType(
                StrictLineGen.rightToLeft(self.res.bottomLeft, walkTopSide=True),
                PositionNode))
            lTop, lBot = longestCommonValues(
                leftTopPoints, leftBottomPoints, lambda x, y: -cmpX(x, y))

            toResize = []
            for i in filterType(GraphVisitor.topDownLeftRightVisitor(lTop), ResourceNode):
                if i.topLeft.point.x() >= self.res.topLeft.point.x():
                    # TODO maybe send to generator to stop
                    continue
                if i.topLeft == lBot:
                    break
                toResize.append(i)

            if right:
                raise NotImplementedError

    def vertical(self, top=False, bottom=False):
        raise NotImplementedError


def cmpX(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.x() - pn2.point.x()


def cmpY(pn1: PositionNode, pn2: PositionNode):
    return pn1.point.y() - pn2.point.y()


T = TypeVar('T')


def longestCommonValues(a: Iterator[T], b: Iterator[T],
                        cmpFun: Callable[[T, T], int]) -> Tuple[T, T]:
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
