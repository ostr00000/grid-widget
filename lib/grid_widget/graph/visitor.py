from operator import methodcaller
from typing import Iterable, Set, TypeVar, Iterator, Callable, Type

from PyQt5.QtCore import QRect

from grid_widget.graph.nodes import PositionNode, ResourceNode, PosAttributes, Node, PosAttr

T = TypeVar('T')


class Filter:
    @staticmethod
    def byType(iterable: Iterable, types: Type[T]) -> Iterable[T]:
        for i in iterable:
            if isinstance(i, types):
                yield i

    @staticmethod
    def byPosX(iterable: Iterable[Node], posX: int) -> Iterable[PositionNode]:
        for i in Filter.byType(iterable, PositionNode):
            if i.point.x() != posX:
                break
            yield i

    @staticmethod
    def byPosY(iterable: Iterable[Node], posY: int) -> Iterable[PositionNode]:
        for i in Filter.byType(iterable, PositionNode):
            if i.point.y() != posY:
                break
            yield i

    @staticmethod
    def byRect(resNodes: Iterable[ResourceNode], rect: QRect):
        for resNode in resNodes:
            if all(rect.contains(posNode.point) for posNode in resNode):
                yield resNode


class BorderGen:
    """
    Default walk side uses square interior
    | <---- ^
    |       |
    V ----> |
    """

    @classmethod
    def rightToLeft(cls, topRight: PositionNode, walkTopSide=False):
        return cls._swapFun(
            topRight, PosAttributes.bottomLeft, PosAttributes.topLeft,
            swap=walkTopSide)

    @classmethod
    def topToDown(cls, topLeft: PositionNode, walkRightSide=True):
        return cls._swapFun(
            topLeft, PosAttributes.bottomLeft, PosAttributes.bottomRight,
            swap=walkRightSide)

    @classmethod
    def leftToRight(cls, bottomLeft: PositionNode, walkTopSide=True):
        return cls._swapFun(
            bottomLeft, PosAttributes.bottomRight, PosAttributes.topRight,
            swap=walkTopSide)

    @classmethod
    def downToTop(cls, bottomRight: PositionNode, walkRightSide=False):
        return cls._swapFun(
            bottomRight, PosAttributes.topLeft, PosAttributes.topRight,
            swap=walkRightSide)

    @classmethod
    def _swapFun(cls, node: PositionNode, pa1: PosAttr, pa2: PosAttr, swap: bool):
        if swap:
            return cls._nodeGen(node, pa2, pa1)
        else:
            return cls._nodeGen(node, pa1, pa2)

    @staticmethod
    def _nodeGen(startNode: Node, resFun: PosAttr, posFun: PosAttr) -> Iterable[Node]:
        if isinstance(startNode, PositionNode):
            yield startNode
            resNode = resFun.attrGetter(startNode)
        else:
            resNode = startNode

        while resNode:
            yield resNode

            if posNode := posFun.attrGetter(resNode):
                yield posNode
            else:
                break

            resNode = resFun.attrGetter(posNode)


class GraphVisitor:
    @staticmethod
    def topDownLeftRightVisitor(topLeft: PositionNode):
        yield from GraphVisitor._graphVisitor(
            Filter.byType(BorderGen.topToDown(topLeft), ResourceNode),
            methodcaller('rightPositionsGen'))

    @staticmethod
    def leftRightTopDown(topLeft: PositionNode):
        yield from GraphVisitor._graphVisitor(
            Filter.byType(BorderGen.leftToRight(topLeft, walkTopSide=False), ResourceNode),
            methodcaller('bottomPositionGen'))

    @staticmethod
    def _graphVisitor(iterable: Iterable[T],
                      nextLevelFun: Callable[[T], Iterator[T]] = None,
                      visited: Set[T] = None) -> Iterable[T]:
        if visited is None:
            visited = set()

        for i in iterable:
            if id(i) in visited:
                continue

            visited.add(id(i))
            if nextLevelFun:
                nextLevelIterator = nextLevelFun(i)
                yield from GraphVisitor._graphVisitor(
                    nextLevelIterator, nextLevelFun, visited)
            yield i
