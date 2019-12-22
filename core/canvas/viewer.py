from PyQt5.QtWidgets import QWidget, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal

from .canvas import Canvas

from utils.log import getLogger
logger = getLogger(1)


def delta2units(delta):
    units = delta / 120  # 8 * 15
    # logger.debug(f"delta: {delta}, units: {units}")
    return units


class ViewerBase(QScrollArea):
    """ 基本Canvas集成单元，本质上是一个包装器：
        - 通过LabelImg::Canvas显示和勾勒图像
        - 利用ImageContainer存储和管理/输出图像
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)

        self.imgr = None
        self.zoom_val = 100
        # self.setBackgroundRole()  # 背景色
        # self.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.setup_canvas()
        self._activate()

    def _activate(self):
        self.scrollChanged.connect(self.on_scroll)
        self.zoomChanged.connect(self.on_zoom)

    def setup_canvas(self):
        self.canvas = Canvas()
        self.setWidget(self.canvas)

    def get_container(self):
        return self.imgr

    def get_image(self):
        return self.canvas.get_image()

    def set_image(self, ndarray):
        self.canvas.set_image(ndarray)
        self.set_fit_window()

    def load_image(self, path_file):
        self.canvas.load_image(path_file)
        self.set_fit_window()

    def wheelEvent(self, event):
        delta = event.angleDelta()
        h_delta = delta.x()
        v_delta = delta.y()
        # if event.orientation() == Qt.Vertical: h_delta = 0

        mods = event.modifiers()
        if Qt.ControlModifier == int(mods) and v_delta:
            self.zoomChanged.emit(v_delta)
        else:
            v_delta and self.scrollChanged.emit(Qt.Vertical, v_delta)
            h_delta and self.scrollChanged.emit(Qt.Horizontal, h_delta)

        event.accept()

    #####################################################################

    def paint_canvas(self):
        self.canvas.scale = 0.01 * self.zoom_val
        self.canvas.adjustSize()
        # logger.debug(f"当前的幕布尺寸：{self.canvas.size()}")
        self.canvas.update()

    def set_fit_origin(self):
        self.zoom_val = 100
        self.paint_canvas()

    def set_fit_window(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2  # So that no scrollbars are generated.
        w1 = self.width() - e
        h1 = self.height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        # w2 = self.canvas.pixmap.width()
        # h2 = self.canvas.pixmap.height()
        w2, h2 = self.canvas.img_size()
        a2 = w2 / h2
        val = w1 / w2 if a2 >= a1 else h1 / h2
        self.zoom_val = int(val * 100)
        self.paint_canvas()

    def set_fit_width(self):
        # The epsilon does not seem to work too well here.
        w = self.width() - 2
        # val = w / self.canvas.pixmap.width()
        val = w / self.canvas.img_size()[0]
        self.zoom_val = int(val * 100)
        self.paint_canvas()

    def on_scroll(self, orientation, delta):
        # logger.debug(f"delta: {delta}, orientation: {orientation}")
        units = delta2units(delta)
        if orientation == Qt.Vertical:
            bar = self.verticalScrollBar()
        else:  # orientation == Qt.Horizontal:
            bar = self.horizontalScrollBar()

        bar.setValue(bar.value() - bar.singleStep() * units)

    def on_zoom(self, delta):
        # zoom in
        units = delta2units(delta)
        scale = 10
        zoom_val = self.zoom_val + scale * units
        if zoom_val < self.MIN_ZOOM_RATIO:  # 设定最小缩放比例
            return
        self.zoom_val = zoom_val
        # logger.debug(f"reset the zoom-scale to: {self.zoom_val}")
        # self.adjust_bar_pos()  # 重定位当前的bar.position
        self.paint_canvas()

    def adjust_bar_pos(self):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.verticalScrollBar()
        v_bar = self.horizontalScrollBar()

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        pos = QCursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.width()
        h = self.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max

        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)
