import os.path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor

from core.canvas.viewer import ScrollViewer, MultiTabViewer

class ScrollCanvas(ScrollViewer):
    """ 增加拖拽和右键菜单 """
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_context_menu()
        self.setAcceptDrops(True)  # 支持拖拽文件

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
        from PyQt5.QtCore import Qt


        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_menu)
        self.contextMenu = QMenu()

        act_fit_origin = self.contextMenu.addAction("图片默认尺寸")
        act_fit_origin.triggered.connect(self.set_fit_origin)

        act_fit_window = self.contextMenu.addAction("匹配窗口尺寸")
        act_fit_window.triggered.connect(self.set_fit_window)

        act_fit_width = self.contextMenu.addAction("匹配窗口宽度")
        act_fit_width.triggered.connect(self.set_fit_width)

        # def drawing_start():
        #     self.canvas.drawing_start()
        #     self.activate_context_menu(False)

        # act_drawing = self.contextMenu.addAction("绘图模式：勾勒轮廓")
        # act_drawing.triggered.connect(drawing_start)

        # self.drawingShapeDone = self.canvas.drawingShapeDone
        # self.drawingShapeDone.connect(lambda: self.activate_context_menu(True))

    def on_right_menu(self):
        self.contextMenu.popup(QCursor.pos())
        self.contextMenu.show()

    def activate_context_menu(self, value):
        if value:
            self.customContextMenuRequested.connect(self.on_right_menu)
        else:
            self.customContextMenuRequested.disconnect(self.on_right_menu)


class MultiTabCanvas(MultiTabViewer):
    def __init__(self, parent):
        super().__init__(parent)
        self.index = -1
        self.addTab()

    def default_name(self):
        self.index += 1
        return f"img_{self.index}"

    def addTab(self, label=None):
        if label is None:
            label = self.default_name()
        widget = ScrollCanvas(self)
        super().addTab(widget, label)

    def removeTab(self, index):
        super().removeTab(index)
        if self.count() == 0:
            self.addTab()
