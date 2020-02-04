from abc import ABC

from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QDrag, QMouseEvent
from PyQt5.QtWidgets import QApplication

from drag_widget.mime.representation import MimeRepresentation


class MimeBaseDragWidget(MimeRepresentation, ABC):
    mimeType: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dragStartPosition = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not (event.buttons().__int__() & Qt.LeftButton):
            return

        dist = QPoint(event.pos() - self.__dragStartPosition).manhattanLength()
        if dist < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimeData = QMimeData()
        self.setDataToMime(mimeData)
        drag.setMimeData(mimeData)
        # drag.setHotSpot(event.pos() - )
        dropAction = drag.exec()
