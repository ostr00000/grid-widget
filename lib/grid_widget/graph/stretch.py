from boltons.cacheutils import cachedproperty

from grid_widget.graph.nodes import ResourceNode, PositionNode
from grid_widget.graph.visitor import StrictLineGen


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
            top = StrictLineGen.rightToLeft(self.res.topLeft, walkTopSide=False)
            bottom = StrictLineGen.rightToLeft(self.res.bottomLeft)

    def vertical(self, top=False, bottom=False):
        pass
