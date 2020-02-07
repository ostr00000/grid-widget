from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Iterable

from PyQt5.QtCore import QPoint
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
        rightBorder = [self.topRight] + self.right + [self.bottomRight]
        for posNode in rightBorder:
            if n := posNode.topRight:
                yield n
            if n := posNode.bottomRight:
                yield n

    def bottomPositionGen(self) -> Iterable[ResourceNode]:
        bottomBorder = [self.bottomLeft] + self.bottom + [self.bottomRight]
        for posNode in bottomBorder:
            if n := posNode.bottomLeft:
                yield n
            if n := posNode.bottomRight:
                yield n

    def __repr__(self):
        return f"{self.widget.objectName()} " \
               f"[({self.topLeft.point.x()}, {self.topLeft.point.y()})," \
               f"({self.bottomRight.point.x()}, {self.bottomRight.point.y()})]"
