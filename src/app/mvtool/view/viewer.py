import os.path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

from core.canvas.viewer import ScrollViewer, MultiTabViewer

class ScrollCanvas(ScrollViewer):
    """ 增加拖拽和右键菜单 """
    def __init__(self, parent):
        super().__init__(parent)
        # self.setup_context_menu()
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

    """
    def setup_context_menu(self):
        # 右键菜单
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
    """

from PyQt5.QtWidgets import QWidget, QStackedLayout, QVBoxLayout
class StackCanvas(QWidget):
    """ 用于多个widget的堆叠放置，如悬浮按钮 """
    def __init__(self, base_widget):
        super().__init__(base_widget.parent())
        self.base = base_widget
        self.layout = QStackedLayout(self)
        self.layout.setStackingMode(QStackedLayout.StackAll)
        self.layout.addWidget(self.base)

        self.base.setWindowFlags(Qt.WindowStaysOnBottomHint)  # 置底
        self.setLayout(self.layout)

    def get_base(self):
        return self.base

    # def addWidget(self, widget):
    #     """ 向当前page页添加控件对象 """
    #     count = self.layout.count()
    #     assert count > 1, "请勿向base页面添加控件, Maybe you shold addPage()"
    #     suspend_layer_wx = self.layout.widget(count - 1)
    #     suspend_layer_wx.addWidget(widget)

    def addPage(self, page):
        """ 增加page页面 """
        self.layout.addWidget(page)
        page.raise_()
        page.setWindowFlags(Qt.WindowStaysOnTopHint)  # 置顶

    def get_container(self):
        return self.base.get_container()

    def get_image(self):
        return self.base.get_container()

    def set_image(self, im_arr):
        return self.base.set_image(im_arr)

    def load_image(self, path_file):
        return self.base.load_image(path_file)


from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QMouseEvent, QIcon
class SuspendLayer(QWidget):
    """ 用于传递事件 """
    margin = 5
    spacing = 3
    btn_size = 24
    def __init__(self, parent, ClassLayout=QVBoxLayout):
        super().__init__(parent)
        layout = ClassLayout(self)
        layout.setContentsMargins(self.margin, self.margin, 0, 0)
        layout.setSpacing(self.spacing)
        self.setLayout(layout)
        self.setFixedWidth(self.btn_size + self.margin)

    def addWidget(self, widget):
        """ 向当前page页添加控件对象 """
        self.layout().addWidget(widget)

    def addButton(self, path_icon, text, slot):
        btn = QPushButton(QIcon(path_icon), "", self)
        btn.clicked.connect(slot)
        btn.setFixedSize(self.btn_size, self.btn_size)
        self.addWidget(btn)

    """
    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)
        # 如当前层需要处理事件，在这里实现
        # ...
        self.PostMouseEventToSiblings(e)

    def PostMouseEventToSiblings(self, e):
        parent = self.parentWidget()
        if parent:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            pt = self.mapTo(parent, e.pos())
            w = parent.childAt(pt)
            if w:
                pt = w.mapFrom(parent, pt)
                event = QMouseEvent(e.type(),
                                    pt,
                                    e.button(),
                                    e.buttons(),
                                    e.modifiers())
                QApplication.postEvent(w, event)

            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
    """

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

        widget = StackCanvas(ScrollCanvas(self))
        page = SuspendLayer(self)
        list_btns = [
            ("app/mvtool/res/zoom.png", "原始尺寸", self.set_fit_origin),
            ("app/mvtool/res/fit-window.png", "适配窗口", self.set_fit_window),
            ("app/mvtool/res/fit-width.png", "适配宽度", self.set_fit_width)
        ]
        for btn_args in list_btns:
            page.addButton(*btn_args)

        nBtns = len(list_btns)
        page.setFixedHeight(SuspendLayer.btn_size * nBtns + (nBtns -1) *
                            SuspendLayer.spacing + SuspendLayer.margin)
        widget.addPage(page)
        super().addTab(widget, label)
        # 跳转到新标签页
        self.setCurrentWidget(widget)

    def set_fit_origin(self):
        viewer = self.currentWidget()
        viewer.base.set_fit_origin()

    def set_fit_window(self):
        viewer = self.currentWidget()
        viewer.base.set_fit_window()

    def set_fit_width(self):
        viewer = self.currentWidget()
        viewer.base.set_fit_width()

    def removeTab(self, index):
        super().removeTab(index)
        if self.count() == 0:
            self.addTab()
