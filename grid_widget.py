import math
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

from drag_widget.image import DragImage
from drag_widget.label import DragLabel
from drag_widget.text import DragText


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)

    def initWidgets(self, widgets: List[QWidget]):
        col = int(math.sqrt(len(widgets)))

        for index, widget in enumerate(widgets):
            widget.setParent(self)
            self.layout.addWidget(widget, int(index / col), index % col)

        # for count in range(self.layout.count()):
        #     if self.layout.itemAt(count).widget() == widget:
        #         break


def main():
    app = QApplication([])

    mw = GridWidget()

    mw.initWidgets([
        DragText('Ala'),
        DragText('ma'),
        DragText('kota'),
        DragImage(pixMap='img.jpg'),
        DragImage(pixMap=Qt.black),
        DragText('ma'),
        DragText('ma'),
        DragImage(pixMap=Qt.green),
        DragText('ma'),
        DragImage(),
        DragLabel('ajdk', Qt.magenta),
        DragLabel('ajdk', 'img.jpg'),
        DragLabel('gfsidhfdhi'),
        DragLabel(),

    ])
    mw.show()
    app.exec()


if __name__ == '__main__':
    main()
