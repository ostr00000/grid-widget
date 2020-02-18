import logging

from PyQt5.QtWidgets import QApplication, QMainWindow

from grid_widget import GridWidget


def main():
    app = QApplication([])

    mmw = QMainWindow()
    mw = GridWidget(mmw)
    mmw.setCentralWidget(mw)
    mmw.show()

    app.exec()


if __name__ == '__main__':
    logging.basicConfig()
    main()
