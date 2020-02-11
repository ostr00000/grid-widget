import logging
from random import randint
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, \
    QFrame

from grid_widget.__init__ import GridWidget


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.num = 0
        self.lastWidget: Optional[QWidget] = None

        self.button = QPushButton("Create widget")
        self.button.clicked.connect(self.onButtonClicked)
        self.verticalLayout.addWidget(self.button)

        self.gridWidget = GridWidget(self)
        self.verticalLayout.addWidget(self.gridWidget)

        # tests
        self.onButtonClicked()
        self.onButtonClicked()
        assert isinstance(self.lastWidget, QWidget)
        self.gridWidget.removeWidget(self.lastWidget)

    def onButtonClicked(self):
        self.num += 1
        frame = QFrame(self)
        frame.setObjectName(f"Frame {self.num}")

        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        frame.setStyleSheet("background-color: rgb({},{},{});".format(*color))
        self.gridWidget.addWidget(frame)
        self.lastWidget = frame


def main():
    app = QApplication([])

    mmw = QMainWindow()
    mw = MyWidget(mmw)
    mmw.setCentralWidget(mw)
    mmw.show()

    app.exec()


if __name__ == '__main__':
    logging.basicConfig()
    main()
