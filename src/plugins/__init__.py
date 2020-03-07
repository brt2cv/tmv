from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__submodule__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
__all__ = __submodule__ + ["ReloadPlugins", "AboutMe"]


import core

from core.plugin.filter import Filter
from utils.base import reload_package

try:
    from mvlib import reload as reload_mvlib
    has_mvlib = True
except ImportError:
    has_mvlib = False

class ReloadPlugins(Filter):
    def run(self):
        if has_mvlib:
            reload_mvlib()  # 重载mvlib依赖

        # _import_submodules(True)  # 重载插件
        reload_package("plugins")
        reload_package("app/triage/plugins")

        # 重载UI
        core.g.get("mwnd").reload_menu()
        core.info("插件已重载...")
        core.g.call("prompt", "插件已重载...")


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
