from traceback import print_exc
from utils.base import singleton, module_class, path2module

from core import alert, g
from . import Plugin
from .filter import DialogFilter
from .adapter import IpyPlugin, PluginAdapter4Ipy

from utils.log import getLogger
logger = getLogger()

# 加载默认的插件
from plugins import *


@singleton
class PluginManager:
    def __init__(self):
        self._cls2ins = {}  # {cls_name: instance}
        self._path2cls = {}  # {path: dict of name2cls}

    def run(self, cls_name):
        try:
            self._cls2ins[cls_name].run()
        except Exception as e:
            alert(str(e))
            print("#"*80)
            print_exc()
            print("#"*80)

    def factory(self, path_module, cls_name):
        # 获取模块中的PluginClass
        if path_module == "plugins":
            plug_cls = eval(cls_name)
        else:
            if path_module not in self._path2cls:
                module = path2module(path_module)
                dict_cls = module_class(module)
                self._path2cls[path_module] = dict_cls
            plug_cls = self._path2cls[path_module][cls_name]

        # 实例化cls
        assert issubclass(plug_cls, Plugin), f"非插件子类：【{cls_name}】"

        if issubclass(plug_cls, IpyPlugin):
            return PluginAdapter4Ipy(plug_cls)
        elif issubclass(plug_cls, DialogFilter):
            return plug_cls(g.get("mwnd"))
        else:
            return plug_cls()

    def load_plugin(self, plugin_info):
        """ plugin_info: str or dict{"path": xxx, "class": yyy}"""
        logger.debug(plugin_info)
        # parse
        if isinstance(plugin_info, str):
            path = "plugins"
            cls_name = plugin_info
        else:  # dict
            path = plugin_info.get("path", "plugins")
            cls_name = plugin_info.get("class")

        plug_obj = self.factory(path, cls_name)
        if cls_name in self._cls2ins:
            logger.warning(f"插件【{cls_name}】已存在，请勿重复导入")
        else:
            self._cls2ins[cls_name] = plug_obj
        return cls_name

    def clear(self):
        self._cls2ins = {}  # {cls_name: instance}
        self._path2cls = {}  # {path: dict of name2cls}
