from PyQt5.QtCore import QObject


class MetaWrapper(type):
    """Add to inherited metaclass function for creating common ancestor.
    A class can have only one metaclass. Moreover metaclass inheritance must be sequential.
    It is especially useful in PyQt, where all object has already metaclass.

    example:
        class MyMeta(MetaWrapper):
            ...

        class MyWidget(QWidget):
            __metaclass__ = MyMeta.wrapMeta(QWidget)
    """

    @classmethod
    def wrapMeta(mcs, classType=type(QObject)):
        if isinstance(classType, type):
            meta = classType
        else:
            meta = type(classType)

        class MetaWrapperInner(mcs, meta):
            pass

        return MetaWrapperInner
