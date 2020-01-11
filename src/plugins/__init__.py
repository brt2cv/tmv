from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__submodule__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
__all__ = __submodule__ + ["ReloadPlugins", "SetMvlibBackend", "AboutMe", "TestPlugin"]


import core
from mvlib import reload as reload_mvlib
from core.plugin.filter import Filter
from utils.base import reload_package
class ReloadPlugins(Filter):
    def run(self):
        reload_mvlib()  # 重载mvlib依赖
        # _import_submodules(True)  # 重载插件
        reload_package("plugins")
        reload_package("app/triage/plugins")

        # 重载UI
        core.g.get("mwnd").reload_menu()
        core.info("插件已重载...")
        core.g.call("prompt", "插件已重载...")


from mvlib import set_backend, get_backend
from core.plugin.filter import DialogFilter
class SetMvlibBackend(DialogFilter):
    title = "切换MVLIB后端"
    buttons = ["OK"]
    view = [{
        "type": "radio",
        "name": "MVLib Backend",
        "val_range": [["pillow", "numpy", "opencv", "scipy", "skimage"]],
        "para": "backend"
    }]

    def accepted(self):
        str_backend = self.widgets["backend"].get_text()
        set_backend(str_backend)
        reload_mvlib()
        core.g.call("prompt", f"Using【{str_backend}】Backend")

    def _set_radio(self, value):
        return self.view[0]["val_range"][0].index(value)

    def run(self):
        if self.needSetupUi:
            self.setup_ui()
            self.needSetupUi = False
        curr_backend = get_backend()
        self.widgets["backend"].set_value(self._set_radio(curr_backend))
        self.show()


from core.plugin import Plugin
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
class AboutMe(Plugin):
    def run(self):
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             "关于",
                             "\n感谢ImagePy的开源，回馈开源社区",
                             parent = core.g.get("mwnd"))
        msgbox.setDetailedText('版权：Bright Li\nTel: 18131218231\nE-mail: brt2@qq.com')
        msgbox.setIconPixmap(QPixmap("app/mvtool/res/logo.png"))
        msgbox.exec_()


from .color import ThresholdPlus
class TestPlugin(ThresholdPlus):
    """ 测试插件 """
