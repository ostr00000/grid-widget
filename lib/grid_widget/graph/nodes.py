from __future__ import annotations

from abc import ABC
from collections import Iterable
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Optional, List, Callable, Iterator

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QWidget


class Node(Iterable, ABC):
    topRight: Node
    topLeft: Node
    bottomLeft: Node
    bottomRight: Node

    def __contains__(self, item):
        return item in (self.topRight, self.topLeft, self.bottomLeft, self.bottomRight)

    def __len__(self):
        return sum((1 for rn in self if rn is not None), 0)


@dataclass
class PosAttr:
    name: str
    opposite: PosAttr = None
    attrGetter: Callable[[Node], Node] = None

    def __post_init__(self):
        self.attrGetter = attrgetter(self.name)

    def __str__(self):
        return self.name


class PosAttributes:
    topRight = PosAttr('topRight')
    bottomLeft = PosAttr('bottomLeft', topRight)
    topRight.opposite = bottomLeft

    topLeft = PosAttr('topLeft')
    bottomRight = PosAttr('bottomRight', topLeft)
    topLeft.opposite = bottomRight


@dataclass
class PositionNode(Node):
    point: QPoint

    topRight: Optional[ResourceNode] = None
    topLeft: Optional[ResourceNode] = None
    bottomLeft: Optional[ResourceNode] = None
    bottomRight: Optional[ResourceNode] = None

    def __iter__(self) -> Iterator[Optional[ResourceNode]]:
        return iter((self.topRight, self.topLeft, self.bottomLeft, self.bottomRight))

    def __str__(self):
        return f"{self.point.x()},{self.point.y()}"


@dataclass
class PositionContainer(Node):
    topRight: PositionNode
    topLeft: PositionNode
    bottomLeft: PositionNode
    bottomRight: PositionNode

    @classmethod
    def fromRect(cls, rect: QRect):
        return PositionContainer(
            PositionNode(rect.topRight()),
            PositionNode(rect.topLeft()),
            PositionNode(rect.bottomLeft()),
            PositionNode(rect.bottomRight()))

    @classmethod
    def fromPositionContainer(cls, posCon: PositionContainer):
        return cls(posCon.topRight, posCon.topLeft,
                   posCon.bottomLeft, posCon.bottomRight)

    def __iter__(self) -> Iterator[PositionNode]:
        return iter((self.topRight, self.topLeft, self.bottomLeft, self.bottomRight))

    def update(self, old: PositionNode, new: PositionNode):
        if old == self.topRight:
            self.topRight = new
        elif old == self.topLeft:
            self.topLeft = new
        elif old == self.bottomLeft:
            self.bottomLeft = new
        elif old == self.bottomRight:
            self.bottomRight = new


@dataclass
class ResourceNode(PositionContainer):
    widget: Optional[QWidget] = None

    top: List[PositionNode] = field(default_factory=list)
    left: List[PositionNode] = field(default_factory=list)
    bottom: List[PositionNode] = field(default_factory=list)
    right: List[PositionNode] = field(default_factory=list)

    def __post_init__(self):
        self.topRight.bottomLeft = self
        self.topLeft.bottomRight = self
        self.bottomLeft.topRight = self
        self.bottomRight.topLeft = self

    def rightPositionsGen(self) -> Iterable[ResourceNode]:
        return self._posGen(self.topRight, self.right, self.bottomRight,
                            PosAttributes.bottomRight, PosAttributes.topRight)

    def leftPositionsGen(self) -> Iterable[ResourceNode]:
        return self._posGen(self.topLeft, self.left, self.bottomLeft,
                            PosAttributes.bottomLeft, PosAttributes.topLeft)

    def bottomPositionGen(self) -> Iterable[ResourceNode]:
        return self._posGen(self.bottomLeft, self.bottom, self.bottomRight,
                            PosAttributes.bottomRight, PosAttributes.bottomLeft)

    def topPositionGen(self) -> Iterable[ResourceNode]:
        return self._posGen(self.topLeft, self.top, self.topRight,
                            PosAttributes.topRight, PosAttributes.topLeft)

    @staticmethod
    def _posGen(pointFirst: PositionNode, points: List[PositionNode],
                pointSecond: PositionNode, posAttrFirst: PosAttr,
                posAttrSecond: PosAttr) -> Iterable[ResourceNode]:
        if n := posAttrFirst.attrGetter(pointFirst):
            yield n

        for posNode in points:
            if n := posAttrSecond.attrGetter(posNode):
                yield n
            if n := posAttrFirst.attrGetter(posNode):
                yield n

        if n := posAttrSecond.attrGetter(pointSecond):
            yield n

    def __str__(self):
        return self.widget.objectName()

    def __repr__(self):
        return f"{self.widget.objectName()} " \
               f"[({self.topLeft.point.x()}, {self.topLeft.point.y()})," \
               f"({self.bottomRight.point.x()}, {self.bottomRight.point.y()})] " \
               f"<{id(self)}>"

    def updateWidget(self):
        self.widget.move(self.topLeft.point)
        rect = QRect(self.topLeft.point, self.bottomRight.point)
        self.widget.resize(rect.width(), rect.height())

    def unpinOthersRelations(self):
        """Remove from all related objects reference to self, self still keep that references"""
        self.topRight.bottomLeft = None
        self.topLeft.bottomRight = None
        self.bottomLeft.topRight = None
        self.bottomRight.topLeft = None

        for otherRelations in (self.top, self.left, self.bottom, self.right):
            for pn in otherRelations:
                if pn.topRight == self:
                    pn.topRight = None
                if pn.topLeft == self:
                    pn.topLeft = None
                if pn.bottomLeft == self:
                    pn.bottomLeft = None
                if pn.bottomRight == self:
                    pn.bottomRight = None

    def hasStrictHorizontalNeighbor(self, left=True, right=True):
        """strict neighbors must have two common positionNodes"""
        if left:
            if otherResource := self.topLeft.bottomLeft:
                if self.topLeft == otherResource.topRight and \
                        self.bottomLeft == otherResource.bottomRight:
                    return True

        if right:
            if otherResource := self.topRight.bottomRight:
                if self.topRight == otherResource.topLeft \
                        and self.bottomRight == otherResource.bottomLeft:
                    return True

        return False

    def strictHorizontalNeighbors(self) -> List[ResourceNode]:
        """self is in middle, split left and right neighbors"""
        foundNodes = []

        node = self
        while node.hasStrictHorizontalNeighbor(right=False):
            node = self.topLeft.bottomLeft
            foundNodes.append(node)

        foundNodes.reverse()
        foundNodes.append(self)

        node = self
        while node.hasStrictHorizontalNeighbor(left=False):
            node = self.topRight.bottomRight
            foundNodes.append(node)

        return foundNodes
