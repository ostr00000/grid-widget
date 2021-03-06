from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QLabel

from drag_widget.mime.base_drag import MimeBaseDragWidget
from drag_widget.mime.base_drop import MimeBaseDropWidget


class DragText(QLabel, MimeBaseDragWidget, MimeBaseDropWidget):
    def isMimeAccepted(self, mime: QMimeData) -> bool:
        return mime.hasText() or super().isMimeAccepted(mime)

    def setDataToMime(self, mime: QMimeData) -> None:
        super().setDataToMime(mime)
        mime.setText(self.text())

    def setDataFromMime(self, mime: QMimeData) -> None:
        super().setDataFromMime(mime)
        self.setText(mime.text())
