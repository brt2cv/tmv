from .base import Canvas, DrawableCanvas
from ..img import ImageContainer, ImageManager

class ViewerBase:
    def load_canvas(self, drawable=False, container="null"):
        """ img_type:
            * null: ImageContainer
            * mgr:  ImageManager
        """
        ClassCanvas = DrawableCanvas if drawable else Canvas
        ClassContainer = {
            "null": ImageContainer,
            "mgr": ImageManager
        }[container]
        self.canvas = ClassCanvas(self, container=ClassContainer())

    def get_container(self):
        return self.canvas.get_container()

    def get_image(self):
        return self.canvas.get_image()

    def set_image(self, ndarray):
        self.canvas.set_image(ndarray)
        self.set_fit_window()

    def load_image(self, path_file):
        self.canvas.load_image(path_file)
        self.set_fit_window()

    def set_fit_window(self):
        """ 将图像缩放到合适尺寸 """
