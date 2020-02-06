from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from drag_widget.mime.base_drag import MimeBaseDragWidget
from drag_widget.mime.base_drop import MimeBaseDropWidget


class DragImage(QLabel, MimeBaseDragWidget, MimeBaseDropWidget):

    def __init__(self, text='', pixMap=None, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        size = 25, 25

        if isinstance(pixMap, str):
            pixMap = QPixmap(pixMap)
            self.setPixmap(pixMap)
        elif isinstance(pixMap, int):
            p = QPixmap(*size)
            p.fill(pixMap)
            self.setPixmap(p)
        else:
            self.setText(text)

    def isMimeAccepted(self, mime: QMimeData) -> bool:
        return mime.hasImage() or super().isMimeAccepted(mime)

    def setDataToMime(self, mime: QMimeData) -> None:
        super().setDataToMime(mime)
        mime.setImageData(self.pixmap())

    def setDataFromMime(self, mime: QMimeData) -> None:
        super().setDataFromMime(mime)
        if mime.hasImage():
            image = mime.imageData()
            if image:
                self.setPixmap(image)
