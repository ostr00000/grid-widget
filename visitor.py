from dataclasses import dataclass, field
from functools import reduce, partial
from operator import attrgetter, methodcaller
from typing import Iterable, Set, TypeVar, Iterator, Callable, Type, Union, Optional, Dict, \
    NamedTuple, Tuple

from nodes import PositionNode, ResourceNode

T = TypeVar('T')


def filterType(iterable: Iterable, types: Type[T]) -> Iterable[T]:
    for i in iterable:
        if isinstance(i, types):
            yield i


NodeType = Union[PositionNode, ResourceNode]


def nodeGen(startNode: NodeType,
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


def graphVisitor(iterable: Iterable[T], nextLevelFun: Callable[[T], Iterator[T]] = None,
                 visited: Set[T] = None) -> Iterable[T]:
    if visited is None:
        visited = set()

    for i in iterable:
        if id(i) in visited:
            continue

        visited.add(id(i))
        if nextLevelFun:
            nextLevelIterator = nextLevelFun(i)
            yield from graphVisitor(nextLevelIterator, nextLevelFun, visited)
        yield i


def leftBorderGen(topNode: PositionNode):
    return nodeGen(topNode, attrgetter('bottomRight'), attrgetter('bottomLeft'))


def rightBorderGen(topNode: PositionNode):
    return nodeGen(topNode, attrgetter('bottomLeft'), attrgetter('bottomRight'))


def topBorderGen(leftNode: PositionNode):
    return nodeGen(leftNode, attrgetter('bottomRight'), attrgetter('topRight'))


def topDownLeftRightVisitor(topLeft: PositionNode):
    yield from graphVisitor(
        filterType(leftBorderGen(topLeft), ResourceNode),
        methodcaller('rightPositionsGen'))


def leftRightTopDown(topLeft: PositionNode):
    yield from graphVisitor(
        filterType(topBorderGen(topLeft), ResourceNode),
        methodcaller('bottomPositionGen'))


TravelDict = Dict[int, int]


def _countMaxColumns(acc: TravelDict, node: ResourceNode) -> TravelDict:
    acc[id(node)] = max(
        (acc.get(id(rp)) for rp in node.rightPositionsGen()),
        default=0) + 1
    return acc


def countMaxColumns(topLeft: PositionNode):
    return reduce(_countMaxColumns, topDownLeftRightVisitor(topLeft), {})


def _countMaxRows(acc: TravelDict, node: ResourceNode) -> TravelDict:
    acc[id(node)] = max(
        (acc.get(id(rp)) for rp in node.bottomPositionGen()),
        default=0) + 1
    return acc


def countMaxRows(topLeft: PositionNode):
    return reduce(_countMaxRows, leftRightTopDown(topLeft), {})


@dataclass
class _BalanceStruct:
    maxColumn: int
    columns: TravelDict
    balanced: TravelDict = field(default_factory=dict)


def _balance(acc: _BalanceStruct, node: ResourceNode,
             childrenNodeFun: Callable[[ResourceNode], Iterator[ResourceNode]]
             ) -> _BalanceStruct:
    myColumn = acc.columns[id(node)]
    for rp in childrenNodeFun(node):
        childColumn = acc.columns[id(rp)]
        diff = myColumn - childColumn
        acc.balanced[id(rp)] = diff

    acc.balanced[id(node)] = acc.maxColumn - myColumn + 1
    return acc


def balanceHorizontal(topLeft: PositionNode, maxColumn: int,
                      columns: TravelDict) -> TravelDict:
    return reduce(
        partial(_balance, childrenNodeFun=methodcaller('rightPositionsGen')),
        topDownLeftRightVisitor(topLeft),
        _BalanceStruct(maxColumn, columns)
    ).balanced


def balanceVertical(topLeft: PositionNode, maxRow: int,
                    rows: TravelDict) -> TravelDict:
    return reduce(
        partial(_balance, childrenNodeFun=methodcaller('bottomPositionGen')),
        leftRightTopDown(topLeft),
        _BalanceStruct(maxRow, rows)
    ).balanced
