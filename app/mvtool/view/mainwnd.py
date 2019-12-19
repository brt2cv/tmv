from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QIcon

from util.base import rpath2curr
from util.log import getLogger
logger = getLogger(1)


class MainWnd(QWidget):
    def __init__(self, parent, attach=None):
        from util.qt5 import loadUi
        from util.gmgr import g

        super().__init__(attach if attach is not None else parent)
        loadUi("ui/wx_viewer.ui", self)
        g.register("mwnd", self)

        self.setProperty("class", "bkg")  # for qss
        self._setup_ui()

        self.setWindowTitle("GUI Demo")
        dir_res = rpath2curr("../res")
        self.setWindowIcon(QIcon(f"{dir_res}/logo.ico"))
        self.resize(600, 450)
        # self.move(0, 0)

    def _setup_ui(self):
        from PyQt5.QtWidgets import QStatusBar, QSizePolicy

        from core.menu import MenubarCreator, ToolbarCreator
        menu_conf = rpath2curr("../config/menu.json")

        menu_creator = MenubarCreator(self)
        menu_creator.load_conf(menu_conf)
        self.ly_header.addWidget(menu_creator.menubar)

        toolbar_creator = ToolbarCreator(self)
        toolbar_creator.load_conf(menu_conf)
        for toolbar in toolbar_creator.list_bars:
            self.ly_header.addWidget(toolbar)

        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("欢迎访问 GUI-Demo")
        self.ly_footer.addWidget(self.status_bar)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.status_bar.setSizePolicy(sizePolicy)

        # Ctrl-Zone:
        # self._setup_ctrl_zone()

        from core.canvas.viewer_scroll import ScrollCanvas, DrawableScrollCanvas
        self.canvas = ScrollCanvas(self, container="mgr")
        self.ly_show.addWidget(self.canvas)

        from util.gmgr import g
        g.register("canvas", self.canvas)
        g.register("prompt", self.status_bar.showMessage, True)

        self._setup_ctrl()

    def _setup_ctrl(self):
        from util.qt5wx.wx_unit import UnitSlider
        slider = UnitSlider(self, "阈值", val_range=[0, 255], isCheckbox=True, isChecked=False)
        self.ly_ctrl.addWidget(slider)

    def save_data(self):
        self.status_bar.showMessage("已储存数据")
