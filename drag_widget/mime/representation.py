import logging
from abc import ABCMeta

from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QWidget
from decorator import decorator

from meta import MetaBaseClassDecorator, runBaseThenInh

logger = logging.getLogger(__name__)


@decorator
def enterExitDec(fun, *args, **kwargs):
    try:
        funName = fun.__wrapped__.__qualname__
    except AttributeError:
        funName = getattr(fun, '__qualname__')

    logger.debug(f"{funName} starting")

    try:
        val = fun(*args, **kwargs)
    except KeyboardInterrupt as e:
        logger.debug(f"{funName} ended with {e}")
        raise
    else:
        logger.debug(f"{funName} ended")
        return val


@decorator
@enterExitDec
def orDec(fun, baseFun=None, *args, **kwargs):
    return fun(*args, **kwargs) or baseFun(*args, **kwargs)


class MimeRepresentation(QWidget, metaclass=MetaBaseClassDecorator.wrapMeta(ABCMeta).wrapMeta()):

    @MetaBaseClassDecorator.decorate(enterExitDec, orDec)
    @enterExitDec
    def isMimeAccepted(self, mime: QMimeData) -> bool:
        return False

    @MetaBaseClassDecorator.decorate(runBaseThenInh)
    def setDataToMime(self, mime: QMimeData) -> None:
        pass

    @MetaBaseClassDecorator.decorate(runBaseThenInh)
    def setDataFromMime(self, mime: QMimeData) -> None:
        pass
