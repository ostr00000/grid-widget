from dataclasses import dataclass, field
from functools import reduce, partial
from operator import methodcaller
from typing import Dict, Any, Callable, Iterator, TypeVar, List

from boltons.cacheutils import cachedproperty

from grid_widget.graph.nodes import ResourceNode, PositionContainer
from grid_widget.graph.visitor import GraphVisitor

T = TypeVar('T')
TravelDict = Dict[int, int]


@dataclass
class _BalanceStruct:
    maxColumn: int
    columns: TravelDict
    balanced: TravelDict = field(default_factory=dict)


class GraphProperties:
    def __init__(self, posCon: PositionContainer, filterNodes: List[ResourceNode] = None):
        self.posCon = posCon
        self._filterNodes = filterNodes

    def acceptNode(self, node: ResourceNode):
        if self._filterNodes is None:
            return True
        return node in self._filterNodes

    @cachedproperty
    def node2ColumnNumber(self) -> TravelDict:
        return reduce(self._countMaxColumns,
                      GraphVisitor.topDownLeftRightVisitor(self.posCon.topLeft), {})

    @staticmethod
    def _countMaxColumns(acc: TravelDict, node: ResourceNode) -> TravelDict:
        acc[id(node)] = max(
            (acc.get(id(rp)) for rp in node.rightPositionsGen()),
            default=0) + 1
        return acc

    @cachedproperty
    def node2RowNumber(self) -> TravelDict:
        return reduce(self._countMaxRows,
                      GraphVisitor.leftRightTopDown(self.posCon.topLeft), {})

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
            GraphVisitor.topDownLeftRightVisitor(self.posCon.topLeft),
            _BalanceStruct(self.maxColumnNumber, self.node2ColumnNumber),
        ).balanced

    @cachedproperty
    def node2VerticalSize(self) -> TravelDict:
        return reduce(
            partial(self._balance, childrenNodeFun=methodcaller('bottomPositionGen')),
            GraphVisitor.leftRightTopDown(self.posCon.topLeft),
            _BalanceStruct(self.maxRowNumber, self.node2RowNumber),
        ).balanced

    def _balance(self, acc: _BalanceStruct, node: ResourceNode,
                 childrenNodeFun: Callable[[ResourceNode], Iterator[ResourceNode]]
                 ) -> _BalanceStruct:
        myColumn = acc.columns[id(node)]
        for rp in childrenNodeFun(node):
            if not self.acceptNode(rp):
                continue

            childColumn = acc.columns[id(rp)]
            diff = myColumn - childColumn
            acc.balanced[id(rp)] = diff

        acc.balanced[id(node)] = acc.maxColumn - myColumn + 1
        return acc
