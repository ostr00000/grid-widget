import logging

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from drag_widget.frame import DragFrame
from grid_widget.__init__ import GridWidget


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
        frame = DragFrame(f"Frame {self.num}")
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
