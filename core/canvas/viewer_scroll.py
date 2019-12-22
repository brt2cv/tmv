from PyQt5.QtWidgets import QWidget, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal

from utils.log import make_logger
logger = make_logger(1)

def delta2units(delta):
    units = delta / 120  # 8 * 15
    # logger.debug(f"delta: {delta}, units: {units}")
    return units

from .viewer import ViewerBase
class ScrollCanvasBase(QScrollArea, ViewerBase):
    zoomChanged = pyqtSignal(int)
    scrollChanged = pyqtSignal(int, int)

    MIN_ZOOM_RATIO = 0.05

    def __init__(self, parent, container="null", drawable=False):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self._member()

        # self.setBackgroundRole()  # 背景色
        # self.setAlignment(Qt.AlignCenter)  # 居中对齐

        self.load_canvas(drawable, container)
        self.setWidget(self.canvas)

        self._activate()

    def _member(self):
        self.zoom_val = 100

    def _activate(self):
        self.scrollChanged.connect(self.on_scroll)
        self.zoomChanged.connect(self.on_zoom)

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


#####################################################################

import os.path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor

class ScrollCanvas(ScrollCanvasBase):
    """ 增加拖拽和右键菜单 """
    def __init__(self, parent, container="null"):
        super().__init__(parent, container, drawable=False)
        self.setup_context_menu()

        # 拖拽文件
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """ 只在进入Window的瞬间触发 """
        event.accept()  # 鼠标放开函数事件

    def dropEvent(self, event):
        path_file = event.mimeData().text().lstrip("file:///")

        _, ext = os.path.splitext(path_file)
        if ext.lower() not in [".png", ".jpg", ".bmp"]:
            QMessageBox.warning(self, "警告", "只支持 png/jpg/bmp 图片文件")
            return
        self.load_image(path_file)

    def setup_context_menu(self):
        """ 右键菜单 """
        from PyQt5.QtWidgets import QMenu

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_menu)
        self.contextMenu = QMenu()

        act_fit_origin = self.contextMenu.addAction("图片默认尺寸")
        act_fit_origin.triggered.connect(self.set_fit_origin)

        act_fit_window = self.contextMenu.addAction("匹配窗口尺寸")
        act_fit_window.triggered.connect(self.set_fit_window)

        act_fit_width = self.contextMenu.addAction("匹配窗口宽度")
        act_fit_width.triggered.connect(self.set_fit_width)

    def on_right_menu(self):
        self.contextMenu.popup(QCursor.pos())
        self.contextMenu.show()

    def set_image(self, ndarray):
        super().set_image(ndarray)


class DrawableScrollCanvas(ScrollCanvas):
    def __init__(self, parent, container="null"):
        super(ScrollCanvas, self).__init__(parent, container, drawable=True)
        self.setup_context_menu()
        self.setAcceptDrops(True)

        self.drawingShapeDone = self.canvas.drawingShapeDone
        self.drawingShapeDone.connect(lambda: self.activate_context_menu(True))

    def setup_context_menu(self):
        super().setup_context_menu()
        act_drawing = self.contextMenu.addAction("绘图模式：勾勒轮廓")

        def drawing_start():
            self.canvas.drawing_start()
            self.activate_context_menu(False)
        act_drawing.triggered.connect(drawing_start)

    def activate_context_menu(self, value):
        if value:
            self.customContextMenuRequested.connect(self.on_right_menu)
        else:
            self.customContextMenuRequested.disconnect(self.on_right_menu)
