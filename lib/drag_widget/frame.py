import logging
import pickle
from dataclasses import dataclass
from random import randint
from typing import cast

from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame

from drag_widget.layout_finder import LayoutFinder
from drag_widget.mime.base_drag import MimeBaseDragWidget
from drag_widget.mime.base_drop import MimeBaseDropWidget

logger = logging.getLogger(__name__)


@dataclass
class DragFrameMime:
    color: QColor
    index: int = None
    swap: bool = True


class DragFrame(QFrame, LayoutFinder, MimeBaseDragWidget, MimeBaseDropWidget):
    DRAG_POSITION = 'internal/dragPosition'

    def __init__(self, parent=None, name='', color: QColor = None):
        super().__init__(parent)
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

        if pl := self.findParentLayout():
            data = DragFrameMime(self.color, pl.indexOf(self))
            mime.setData(self.DRAG_POSITION, pickle.dumps(data))

    def setDataFromMime(self, mime: QMimeData) -> None:
        super().setDataFromMime(mime)

        if d := mime.data(self.DRAG_POSITION):
            data: DragFrameMime = pickle.loads(d)
            if data.swap and data.index != -1:
                if pl := self.findParentLayout():
                    try:
                        widget = pl.itemAt(data.index).widget()
                        widget = cast(DragFrame, widget)
                        widget._setColor(self.color)
                    except AttributeError as err:
                        logger.error(err)

            self._setColor(data.color)
