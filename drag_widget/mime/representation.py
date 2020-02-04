from abc import ABCMeta

from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QWidget
from decorator import decorator

from meta import MetaBaseClassDecorator, runBaseThenInh


@decorator
def orDec(fun, baseFun=None, *args, **kwargs):
    return fun(*args, **kwargs) or baseFun(*args, **kwargs)

c = 0

class MimeRepresentation(QWidget, metaclass=MetaBaseClassDecorator.wrapMeta(ABCMeta).wrapMeta()):

    @MetaBaseClassDecorator.decorate(runBaseThenInh)
    @MetaBaseClassDecorator.decorate(orDec)
    def isMimeAccepted(self, mime: QMimeData) -> bool:
        global c
        c += 1
        return False

    @MetaBaseClassDecorator.decorate(runBaseThenInh)
    def setDataToMime(self, mime: QMimeData) -> None:
        pass

    @MetaBaseClassDecorator.decorate(runBaseThenInh)
    def setDataFromMime(self, mime: QMimeData) -> None:
        pass
