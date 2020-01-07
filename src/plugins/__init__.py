from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__submodule__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
__all__ = __submodule__ + ["ReloadPlugins", "AboutMe"]

def _all_modules():
    from pprint import pprint
    print("All sub-modules:")
    pprint(__all__)


import importlib
def _import_submodules(isReload=False):
    def dynamic_import(submodule: str):
        module = importlib.import_module(submodule, __package__)
        if isReload:
            importlib.reload(module)

    for str_module in __submodule__:
        dynamic_import("." + str_module)


import core
from mvlib import reload as reload_mvlib
from core.plugin.filter import Filter
class ReloadPlugins(Filter):
    def run(self):
        reload_mvlib()  # 重载mvlib依赖
        _import_submodules(True)  # 重载插件

        # 重载UI
        core.g.get("mwnd")._setup_menu(isReload=True)
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
