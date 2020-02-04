from abc import ABC

from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from drag_widget.mime.representation import MimeRepresentation


class MimeBaseDropWidget(MimeRepresentation, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self.isMimeAccepted(event.mimeData()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        mimeData = event.mimeData()
        if self.isMimeAccepted(mimeData):
            self.setDataFromMime(mimeData)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
