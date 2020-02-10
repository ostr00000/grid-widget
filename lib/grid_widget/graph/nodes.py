from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Iterable

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QWidget


@dataclass
class Node:
    pass


@dataclass
class PositionNode(Node):
    point: QPoint

    topRight: Optional[ResourceNode] = None
    topLeft: Optional[ResourceNode] = None
    bottomLeft: Optional[ResourceNode] = None
    bottomRight: Optional[ResourceNode] = None


@dataclass
class ResourceNode:
    topRight: PositionNode
    topLeft: PositionNode
    bottomLeft: PositionNode
    bottomRight: PositionNode

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
        if n := self.topRight.bottomRight:
            yield n

        for posNode in self.right:
            if n := posNode.topRight:
                yield n
            if n := posNode.bottomRight:
                yield n

        if n := self.bottomRight.topRight:
            yield n

    def bottomPositionGen(self) -> Iterable[ResourceNode]:
        if n := self.bottomLeft.bottomRight:
            yield n

        for posNode in self.bottom:
            if n := posNode.bottomLeft:
                yield n
            if n := posNode.bottomRight:
                yield n

        if n := self.bottomRight.bottomLeft:
            yield n

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
