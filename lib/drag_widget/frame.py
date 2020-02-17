import pickle
from dataclasses import dataclass
from random import randint
from typing import cast

from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QGridLayout

from drag_widget.mime.base_drag import MimeBaseDragWidget
from drag_widget.mime.base_drop import MimeBaseDropWidget


@dataclass
class DragFrameMime:
    color: QColor
    index: int = None


class DragFrame(QFrame, MimeBaseDragWidget, MimeBaseDropWidget, ):
    DRAG_POSITION = 'internal/dragPosition'

    def __init__(self, name, color: QColor = None):
        super().__init__()
        self.setObjectName(name)

        if color is None:
            color = QColor(randint(0, 255), randint(0, 255), randint(0, 255))
        self._setColor(color)

    def _setColor(self, color: QColor):
        self.color = color
        self.setStyleSheet("background-color: rgb({},{},{});".format(
            color.red(), color.green(), color.blue()))

    def isMimeAccepted(self, mime: QMimeData) -> bool:
        return mime.hasFormat(self.DRAG_POSITION) or super().isMimeAccepted(mime)

    def setDataToMime(self, mime: QMimeData) -> None:
        super().setDataToMime(mime)

        if p := self.parent():
            if lay := p.layout():
                data = DragFrameMime(self.color, lay.indexOf(self))
                mime.setData(self.DRAG_POSITION, pickle.dumps(data))

    def setDataFromMime(self, mime: QMimeData) -> None:
        super().setDataFromMime(mime)

        if d := mime.data(self.DRAG_POSITION):
            data: DragFrameMime = pickle.loads(d)
            if p := self.parent():
                if lay := p.layout():
                    lay = cast(QGridLayout, lay)
                    if item := lay.itemAt(data.index):
                        if widget := item.widget():
                            widget = cast(DragFrame, widget)
                            widget._setColor(self.color)

            self._setColor(data.color)
