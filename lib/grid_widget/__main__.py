import logging
from random import randint, shuffle
from typing import Optional, List

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, \
    QFrame

from grid_widget.__init__ import GridWidget


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalLayout = QVBoxLayout(self)
        self.num = 0
        self.createdWidgets: List[QWidget] = []

        self.createButton = QPushButton("Create widget")
        self.createButton.clicked.connect(self.onCreateClicked)
        self.verticalLayout.addWidget(self.createButton)

        self.deleteButton = QPushButton("Delete widget")
        self.deleteButton.clicked.connect(self.onDeleteClicked)
        self.verticalLayout.addWidget(self.deleteButton)

        self.gridWidget = GridWidget(self)
        self.verticalLayout.addWidget(self.gridWidget)

        # tests
        self.onCreateClicked()
        self.onCreateClicked()
        self.gridWidget.removeWidget(self.createdWidgets[-1])

    def onCreateClicked(self):
        self.num += 1
        frame = QFrame(self)
        frame.setObjectName(f"Frame {self.num}")

        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        frame.setStyleSheet("background-color: rgb({},{},{});".format(*color))
        self.gridWidget.addWidget(frame)
        self.createdWidgets.append(frame)

    def onDeleteClicked(self):
        shuffle(self.createdWidgets)
        try:
            widget = self.createdWidgets.pop()
        except IndexError:
            pass
        else:
            self.gridWidget.removeWidget(widget)


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
