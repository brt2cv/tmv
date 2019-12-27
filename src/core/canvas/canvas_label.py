from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from .base import ICanvas

class ImageLabel(QLabel, ICanvas):
    def __init__(self, parent, container=None):
        super().__init__(parent)
        super(ImageLabel, ICanvas).__init__(container)

    def set_image(self, im_arr, size=None):
        super().set_image(im_arr)
        if size is None:
            h, w = im_arr.shape[:2]
            size = (w, h)
        self.set_size(*size)

    def set_size(self, width, height, scale_type=Qt.IgnoreAspectRatio):
        pixmap = self.get_pixmap()
        pixmap = pixmap.scaled(width, height, scale_type)
        self.setPixmap(pixmap)
