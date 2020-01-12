from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from utils.base import rpath2curr
from core import getLogger
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

        from core import conf_mgr

        self.setWindowTitle("MVTool图像编辑器")
        path_icon = conf_mgr.get("app", "gui", "icon")
        self.setWindowIcon(QIcon(path_icon))

        win_size = conf_mgr.get("app", "gui", "win_size")
        x, y = win_size.split(",")
        self.resize(int(x), int(y))
        # self.move(0, 0)

    def _setup_ui(self):
        from PyQt5.QtWidgets import QStatusBar, QSizePolicy

        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("欢迎访问 MVTool 图像编辑器")
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

    def _setup_menu(self):
        """ 菜单栏和工具栏的加载 """
        from core import menu
        menu_conf = rpath2curr("../config/menu.json")

        menu_creator = menu.MenubarCreator(self)
        menu_creator.load_conf(menu_conf)
        self.ly_header.addWidget(menu_creator.menubar)

        toolbar_creator = menu.ToolbarCreator(self)
        toolbar_creator.load_conf(menu_conf)
        for toolbar in toolbar_creator.list_bars:
            toolbar.setOrientation(Qt.Vertical)
            self.ly_sidebar.addWidget(toolbar)

    def reload_menu(self):
        from core import menu

        from core.plugin.mgr import PluginManager
        plug_mgr = PluginManager()
        plug_mgr.clear()  # 清除原有的plugin实例

        from importlib import reload
        reload(menu)

        import plugins
        reload(plugins)

        # 清理ly_header
        from utils.qt5 import clear_layout
        clear_layout(self.ly_header)
        clear_layout(self.ly_sidebar)

        self._setup_menu()

    def _setup_ctrl(self):
        from utils.qt5wx.wx_unit import UnitSlider
        slider = UnitSlider(self, "阈值", val_range=[0, 255], isCheckbox=True, isChecked=False)
        self.ly_ctrl.addWidget(slider)
