from dataclasses import dataclass, field
from functools import reduce, partial
from operator import methodcaller
from typing import Dict, Any, Callable, Iterator, TypeVar

from boltons.cacheutils import cachedproperty

from nodes import PositionNode, ResourceNode
from visitor import GraphVisitor

T = TypeVar('T')
TravelDict = Dict[int, int]


@dataclass
class _BalanceStruct:
    maxColumn: int
    columns: TravelDict
    balanced: TravelDict = field(default_factory=dict)


class GraphProperties:
    def __init__(self, topLeft: PositionNode):
        self.topLeft = topLeft

    @cachedproperty
    def node2ColumnNumber(self) -> TravelDict:
        return reduce(self._countMaxColumns,
                      GraphVisitor.topDownLeftRightVisitor(self.topLeft), {})

    @staticmethod
    def _countMaxColumns(acc: TravelDict, node: ResourceNode) -> TravelDict:
        acc[id(node)] = max(
            (acc.get(id(rp)) for rp in node.rightPositionsGen()),
            default=0) + 1
        return acc

    @cachedproperty
    def node2RowNumber(self) -> TravelDict:
        return reduce(self._countMaxRows,
                      GraphVisitor.leftRightTopDown(self.topLeft), {})

    @staticmethod
    def _countMaxRows(acc: TravelDict, node: ResourceNode) -> TravelDict:
        acc[id(node)] = max(
            (acc.get(id(rp)) for rp in node.bottomPositionGen()),
            default=0) + 1
        return acc

    @cachedproperty
    def maxColumnNumber(self) -> int:
        return self._maxValueFromDict(self.node2ColumnNumber)

    @cachedproperty
    def maxRowNumber(self) -> int:
        return self._maxValueFromDict(self.node2RowNumber)

    @staticmethod
    def _maxValueFromDict(dictionary: Dict[Any, T]) -> T:
        return dictionary[max(dictionary, key=dictionary.get)]

    @cachedproperty
    def node2horizontalSize(self) -> TravelDict:
        return reduce(
            partial(self._balance, childrenNodeFun=methodcaller('rightPositionsGen')),
            GraphVisitor.topDownLeftRightVisitor(self.topLeft),
            _BalanceStruct(self.maxColumnNumber, self.node2ColumnNumber),
        ).balanced

    @cachedproperty
    def node2VerticalSize(self) -> TravelDict:
        return reduce(
            partial(self._balance, childrenNodeFun=methodcaller('bottomPositionGen')),
            GraphVisitor.leftRightTopDown(self.topLeft),
            _BalanceStruct(self.maxRowNumber, self.node2RowNumber),
        ).balanced

    @staticmethod
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
