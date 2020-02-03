import typing

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, \
    QPushButton, QLineEdit, QLabel
from matplotlib.backend_bases import MouseButton


class ReceiveData(QLineEdit):

    def __init__(self, text='', parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        text = event.mimeData().text()
        self.setText(text)
        event.acceptProposedAction()


class DragData(QLabel):

    def __init__(self):
        super().__init__()
        self.dragStartPosition = None
        self.setText("Label")

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not (event.buttons().__int__() & Qt.LeftButton):
            return

        dist = QPoint(event.pos() - self.dragStartPosition).manhattanLength()
        if dist < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mineData = QMimeData()

        mineData.setText("ala")
        drag.setMimeData(mineData)

        dropAction = drag.exec()


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QGridLayout(self)

    def addWidget(self, widget):
        widget.setParent(self)
        self.layout.addWidget(widget, )


def main():
    app = QApplication([])

    mw = GridWidget()
    mw.addWidget(DragData())
    mw.addWidget(ReceiveData("Press me"))

    mw.show()
    app.exec()


if __name__ == '__main__':
    main()
