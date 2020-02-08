from operator import attrgetter, methodcaller
from typing import Iterable, Set, TypeVar, Iterator, Callable, Type, Union, Optional

from grid_widget.graph.nodes import PositionNode, ResourceNode

T = TypeVar('T')
NodeType = Union[PositionNode, ResourceNode]


def filterType(iterable: Iterable, types: Type[T]) -> Iterable[T]:
    for i in iterable:
        if isinstance(i, types):
            yield i


class BorderGen:
    @staticmethod
    def left(topLeft: PositionNode):
        return BorderGen._nodeGen(
            topLeft, attrgetter('bottomRight'), attrgetter('bottomLeft'))

    @staticmethod
    def right(topRight: PositionNode):
        return BorderGen._nodeGen(
            topRight, attrgetter('bottomLeft'), attrgetter('bottomRight'))

    @staticmethod
    def top(topLeft: PositionNode):
        return BorderGen._nodeGen(
            topLeft, attrgetter('bottomRight'), attrgetter('topRight'))

    @staticmethod
    def bottom(bottomLeft: PositionNode):
        return BorderGen._nodeGen(
            bottomLeft, attrgetter('topRight'), attrgetter('bottomRight'))

    @staticmethod
    def _nodeGen(startNode: NodeType,
                 resFun: Callable[[PositionNode], Optional[ResourceNode]],
                 posFun: Callable[[ResourceNode], Optional[PositionNode]],
                 ) -> Iterable[NodeType]:
        if isinstance(startNode, PositionNode):
            yield startNode
            resNode = resFun(startNode)
        else:
            resNode = startNode

        while resNode:
            yield resNode

            if posNode := posFun(resNode):
                yield posNode
            else:
                break

            resNode = resFun(posNode)


class GraphVisitor:
    @staticmethod
    def topDownLeftRightVisitor(topLeft: PositionNode):
        yield from GraphVisitor._graphVisitor(
            filterType(BorderGen.left(topLeft), ResourceNode),
            methodcaller('rightPositionsGen'))

    @staticmethod
    def leftRightTopDown(topLeft: PositionNode):
        yield from GraphVisitor._graphVisitor(
            filterType(BorderGen.top(topLeft), ResourceNode),
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
