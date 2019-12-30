from .file import *
from .edit import *
from .view import *
from .color import *
from .morphology import *


from utils.gmgr import g
from core.plugin.filter import Filter, DialogFilterBase
from core.plugin.adapter import IpyPlugin, PluginAdapter4Ipy
def export_plugin(cls_name: str):
    plug_cls = eval(cls_name)
    assert issubclass(plug_cls, Filter) or issubclass(plug_cls, IpyPlugin),\
           f"未知的插件类型，非【Filter】的子类：【{cls_name}】"

    # factory
    if issubclass(plug_cls, IpyPlugin):
        return PluginAdapter4Ipy(plug_cls)
    elif issubclass(plug_cls, DialogFilterBase):
        return plug_cls(g.get("mwnd"))
    else:
        return plug_cls()


from importlib import reload, import_module
class ReloadPlugins(Filter):
    def reload_module(self, submodule: str):
        module = import_module(submodule, __package__)
        reload(module)

    def run(self):
        self.reload_module(".file")
        self.reload_module(".edit")
        self.reload_module(".view")
        self.reload_module(".color")
        self.reload_module(".morphology")
        g.get("mwnd")._setup_menu(isReload=True)


from PyQt5.QtWidgets import QMessageBox
class AboutMe(Filter):
    def run(self):
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             "关于",
                             "感谢ImagePy的开源，回馈开源社区",
                             parent = g.get("mwnd"))
        msgbox.setDetailedText('版权：Bright Li\nTel: 18131218231\nE-mail: brt2@qq.com')
        msgbox.setIconPixmap(QPixmap("app/mvtool/res/logo.png"))
        msgbox.exec_()
