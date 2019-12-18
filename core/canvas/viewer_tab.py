from PyQt5.QtWidgets import QTableWidget
from core.ui.scroll_canvas import ImageScrollCanvas

from core.canvas.interface import ICanvas
class MultiTabCanvas(QTableWidget, ICanvas):
    """ 支持多标签的Canvas """
    def __init__(self, parent, page_cls):
        super().__init__(parent)
        self.page_cls = page_cls

    def addTab(self, label):
        page = self.page_cls(self)
        super().addTab(page, label)

    def get_image(self):
