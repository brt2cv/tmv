from .demo import *

import core
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
        return plug_cls(core.g.get("mwnd"))
    else:
        return plug_cls()
