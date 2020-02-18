from PyQt5.QtWidgets import QWidget, QLayout


class LayoutFinder(QWidget):

    def findParentLayout(self):
        if parent := self.parent():
            if lay := parent.layout():
                return self._findParentLayout(lay)

        return None

    def _findParentLayout(self, layout: QLayout):
        if layout.indexOf(self) >= 0:
            return layout

        for child in layout.children():  # type: QLayout
            if lay := self._findParentLayout(child):
                return lay

        return None
