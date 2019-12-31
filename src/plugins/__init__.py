from PyQt5.QtWidgets import QMessageBox

from .file import *
from .edit import *
from .view import *
from .color import *
from .morphology import *


from utils.gmgr import g
from core.plugin import Plugin
from core.plugin.filter import Filter
from core.plugin.adapter import IpyPlugin, PluginAdapter4Ipy
def export_plugin(cls_name: str):
    plug_cls = eval(cls_name)
    assert issubclass(plug_cls, Plugin), f"非插件子类：【{cls_name}】"

    # factory
    if issubclass(plug_cls, IpyPlugin):
        return PluginAdapter4Ipy(plug_cls)
    elif issubclass(plug_cls, DialogFilter):
        return plug_cls(g.get("mwnd"))
    else:
        return plug_cls()


class ReloadPlugins(Filter):
    def run(self):
        # 重载mvlib依赖
        from mvlib import reload_mvlib
        reload_mvlib()

        # 重载插件
        from importlib import reload, import_module

        def reload_module(submodule: str):
            module = import_module(submodule, __package__)
            reload(module)

        reload_module(".file")
        reload_module(".edit")
        reload_module(".view")
        reload_module(".color")
        reload_module(".morphology")

        # 重载UI
        g.get("mwnd")._setup_menu(isReload=True)
        QMessageBox.information(g.get("mwnd"), "通知", "插件已重载...")
        g.call("prompt", "插件已重载...")


class AboutMe(Plugin):
    def run(self):
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             "关于",
                             "\n感谢ImagePy的开源，回馈开源社区",
                             parent = g.get("mwnd"))
        msgbox.setDetailedText('版权：Bright Li\nTel: 18131218231\nE-mail: brt2@qq.com')
        msgbox.setIconPixmap(QPixmap("app/mvtool/res/logo.png"))
        msgbox.exec_()
