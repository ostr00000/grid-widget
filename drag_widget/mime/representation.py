import logging
from abc import ABCMeta

from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QWidget

from meta import MetaBaseClassDecorator

logger = logging.getLogger(__name__)


class MimeRepresentation(QWidget, metaclass=MetaBaseClassDecorator.wrapMeta(ABCMeta).wrapMeta()):
    """Base class to drag mime"""

    def isMimeAccepted(self, mime: QMimeData) -> bool:
        return False

    def setDataToMime(self, mime: QMimeData) -> None:
        pass

    def setDataFromMime(self, mime: QMimeData) -> None:
        pass
