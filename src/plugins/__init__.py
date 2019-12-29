from .file import *
from .edit import *
from .color import *
from .morphology import *


from utils.gmgr import g
from core.plugin.filter import Filter, DialogFilter
from core.plugin.adapter import IpyPlugin, PluginAdapter4Ipy
def export_plugin(cls_name: str):
    plug_cls = eval(cls_name)
    assert issubclass(plug_cls, Filter) or issubclass(plug_cls, IpyPlugin),\
           f"未知的插件类型，非【Filter】的子类：【{cls_name}】"

    # factory
    if issubclass(plug_cls, IpyPlugin):
        return PluginAdapter4Ipy(plug_cls)
    elif issubclass(plug_cls, DialogFilter):
        return plug_cls(g.get("mwnd"))
    else:
        return plug_cls()


class ReloadPlugins(Filter):
    def run(self):
        from . import file
        from . import edit
        from . import color
        from . import morphology
        from importlib import reload

        reload(file)
        reload(edit)
        reload(color)
        reload(morphology)

        g.get("mwnd")._setup_menu(isReload=True)
