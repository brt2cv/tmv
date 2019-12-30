from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from utils.base import rpath2curr
from utils.log import getLogger
logger = getLogger(1)


class MainWnd(QWidget):
    def __init__(self, parent, attach=None):
        from utils.qt5 import loadUi
        from utils.gmgr import g

        super().__init__(attach if attach is not None else parent)
        loadUi("ui/wx_mwnd.ui", self)
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

        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("欢迎访问 GUI-Demo")
        self.ly_footer.addWidget(self.status_bar)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.status_bar.setSizePolicy(sizePolicy)

        # Ctrl-Zone:
        # self._setup_ctrl_zone()

        from .viewer import TabCanvas
        self.canvas = TabCanvas(self)
        self.ly_show.addWidget(self.canvas)

        from utils.gmgr import g
        g.register("canvas", self.canvas)

        def promp_in_second(message, timeout=0):
            """ 使用'秒'为单位显示图像 """
            self.status_bar.showMessage(message, timeout*1000)
        g.register("prompt", promp_in_second, True)

        self._setup_menu()
        # self._setup_ctrl()

    def _setup_menu(self, isReload=False):
        """ 菜单栏和工具栏的加载 """
        from core import menu
        if isReload:
            from importlib import reload
            reload(menu)

            import plugins
            reload(plugins)

            # 清理ly_header
            from utils.qt5 import clear_layout
            clear_layout(self.ly_header)
            clear_layout(self.ly_sidebar)

        menu_conf = rpath2curr("../config/menu.json")

        menu_creator = menu.MenubarCreator(self)
        menu_creator.load_conf(menu_conf)
        self.ly_header.addWidget(menu_creator.menubar)

        toolbar_creator = menu.ToolbarCreator(self)
        toolbar_creator.load_conf(menu_conf)
        for toolbar in toolbar_creator.list_bars:
            toolbar.setOrientation(Qt.Vertical)
            self.ly_sidebar.addWidget(toolbar)

    def _setup_ctrl(self):
        from utils.qt5wx.wx_unit import UnitSlider
        slider = UnitSlider(self, "阈值", val_range=[0, 255], isCheckbox=True, isChecked=False)
        self.ly_ctrl.addWidget(slider)
