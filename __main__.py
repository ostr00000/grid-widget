import logging
from random import randint

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, \
    QFrame

from grid_widget import GridWidget


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.num = 0

        self.button = QPushButton("Create widget")
        self.button.clicked.connect(self.onButtonClicked)
        self.verticalLayout.addWidget(self.button)

        self.gridWidget = GridWidget(self)
        self.verticalLayout.addWidget(self.gridWidget)

        self.onButtonClicked()
        self.onButtonClicked()

    def onButtonClicked(self):
        self.num += 1
        frame = QFrame(self)
        frame.setObjectName(f"Frame {self.num}")

        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        frame.setStyleSheet("background-color: rgb({},{},{});".format(*color))
        self.gridWidget.addWidget(frame)


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
