from drag_widget.image import DragImage
from drag_widget.text import DragText


class DragLabel(DragText, DragImage):


    def isMimeAccepted(self, mime) -> bool:
        pass

