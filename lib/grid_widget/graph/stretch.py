from typing import TypeVar, Tuple, Callable, Iterable, List

from PyQt5.QtCore import QRect
from boltons.cacheutils import cachedproperty

from grid_widget import Distributor
from grid_widget.graph.nodes import ResourceNode, PositionNode, PositionContainer
from grid_widget.graph.visitor import Filter, GraphVisitor, BorderGen
import logging

logger = logging.getLogger(__name__)
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
        self.distributeCorners = PositionContainer.fromPositionContainer(remNode)

        self.removedPosNodes = []
        self.nodesToResize = []

    def stretch(self):
        topRight = PositionNodeProperties(self.remNode.topRight)
        topLeft = PositionNodeProperties(self.remNode.topLeft)
        bottomLeft = PositionNodeProperties(self.remNode.bottomLeft)
        bottomRight = PositionNodeProperties(self.remNode.bottomRight)

        if topRight.h and topLeft.h and bottomLeft.h and bottomRight.h:
            self.findLeftNodes()
            self.findRightNodes()

        elif topRight.v and topLeft.v and bottomLeft.v and bottomRight.v:
            raise NotImplementedError

        elif topRight.h and bottomRight.h:
            self.findRightNodes()
            self.moveRelationsRight()
            self.distributeCorners.topLeft = self.remNode.topLeft
            self.distributeCorners.bottomLeft = self.remNode.bottomLeft

        elif topLeft.h and bottomLeft.h:
            self.findLeftNodes()
            self.moveRelationsLeft()
            self.distributeCorners.topRight = self.remNode.topRight
            self.distributeCorners.bottomRight = self.remNode.bottomRight

        elif topRight.v and topLeft.v:
            raise NotImplementedError

        elif bottomRight.v and bottomLeft.v:
            raise NotImplementedError

        else:  # is it possible? yes
            # leave resource node without widget
            raise NotImplementedError

        distributor = Distributor(self.distributeCorners, filterNodes=self.nodesToResize)
        distributor.distribute(QRect(self.distributeCorners.topLeft.point,
                                     self.distributeCorners.bottomRight.point))

    def findLeftNodes(self):
        logger.debug('finding Left')  # DEBUG
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

        self.distributeCorners.topLeft = lTop
        self.distributeCorners.bottomLeft = lBot

    def findRightNodes(self):
        logger.debug('finding Right')  # DEBUG

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
            GraphVisitor.topDownLeftRightVisitor(self.remNode.topRight),
            QRect(self.remNode.topRight.point, rBot.point)))
        self.nodesToResize.extend(nodeToResize)

        self.distributeCorners.topRight = rTop
        self.distributeCorners.bottomRight = rBot

    def moveRelationsLeft(self):  # TODO move method to ResNode
        firstLeft = self.remNode.topLeft.bottomLeft
        firstLeft.top.append(firstLeft.topRight)
        firstLeft.topRight = self.remNode.topRight
        firstLeft.topRight.bottomLeft = firstLeft

        firstLeft = self.remNode.bottomLeft.topLeft
        firstLeft.bottom.append(firstLeft.bottomRight)
        firstLeft.bottomRight = self.remNode.bottomRight
        firstLeft.bottomRight.topLeft = firstLeft

    def moveRelationsRight(self):
        firstRight = self.remNode.topRight.bottomRight
        firstRight.top.insert(0, firstRight.topLeft)
        firstRight.topLeft = self.remNode.topLeft
        firstRight.topLeft.bottomRight = firstRight

        firstRight = self.remNode.bottomRight.topRight
        firstRight.bottom.insert(0, firstRight.bottomLeft)
        firstRight.bottomLeft = self.remNode.bottomLeft
        firstRight.bottomLeft.topRight = firstRight


CMP_SNAP = 1


def cmpX(pn1: PositionNode, pn2: PositionNode):
    return 0 if abs(x := pn1.point.x() - pn2.point.x()) <= CMP_SNAP else x


def cmpY(pn1: PositionNode, pn2: PositionNode):
    return 0 if abs(y := pn1.point.y() - pn2.point.y()) <= CMP_SNAP else y


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
