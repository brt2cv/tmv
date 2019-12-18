# 罗列了关于menu.json解析相关类
from util.log import getLogger
logger = getLogger()

from util.base import singleton
from util.gmgr import g
from .plugin import import_plugin
from .plugin.features import FeatureTypeError
from .plugin.filter import Filter, DialogFilter


@singleton
class PluginManager:
    def __init__(self):
        self.dict_plugins = {}  # cls_name: instance

    def run(self, cls_name):
        try:
            self.dict_plugins[cls_name].run()
        except FeatureTypeError:
            pass

    def load_plugin(self, plugin_info):
        """ plugin_info: str or dict{"path": xxx, "class": yyy}"""
        # parse
        if isinstance(plugin_info, str):
            path = "plugins"
            cls_name = plugin_info
        else:  # dict
            path = plugin_info.get("path", "plugins")
            cls_name = plugin_info.get("class")

        plug_cls = import_plugin(path, cls_name)
        key = plug_cls.__name__
        if key in self.dict_plugins:
            logger.warning(f"插件【{key}】已存在，请勿重复导入")
            return key

        # factory
        if issubclass(plug_cls, DialogFilter):
            instance = plug_cls(g.get("mwnd"))
        elif issubclass(plug_cls, Filter):
            instance = plug_cls()
        else:
            raise Exception(f"未知的Plugin类型：【{plug_cls}】")

        self.dict_plugins[key] = instance
        return key

plug_mgr = PluginManager()

#####################################################################

from util.qt5 import make_action, make_submenu

def add_action(parent_menu, dict_member):
    plug_info = dict_member.get("plugin")
    if plug_info:
        plug_name = plug_mgr.load_plugin(plug_info)
        func_slot = lambda: plug_mgr.run(plug_name)
    else:
        logger.warning(f"按钮【{dict_member['name']}】未定义操作")
        func_slot = None

    make_action(parent_menu,
                dict_member["name"],
                func_slot,
                dict_member.get("icon"),
                dict_member.get("shortcut"),
                dict_member.get("description"))

class MenubarCreator:
    def __init__(self, parent):
        from PyQt5.QtWidgets import QMenuBar
        self.menubar = QMenuBar(parent)

    def load_conf(self, path_conf):
        import json
        # self.dict_menu = {self.menubar: {}}
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        assert "menubar" in dict_conf, '格式错误，未发现【"menubar"】项，无法导入按钮'
        for menu_group_info in dict_conf["menubar"]:
            self.make_node(self.menubar, menu_group_info)

    def make_node(self, parent_menu, dict_info):
        if "members" in dict_info:
            node_name = dict_info["name"]
            submenu = make_submenu(parent_menu, node_name)
            # 展开submenu
            for elem in dict_info["members"]:  # 递归
                self.make_node(submenu, elem)
        else:
            add_action(parent_menu, dict_info)


#####################################################################
from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon

class ToolbarCreator:
    def __init__(self, parent):
        self.parent = parent
        self.list_bars = []

    def load_conf(self, path_conf):
        import json

        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        assert "toolbar" in dict_conf, '格式错误，未发现【"toolbar"】项，无法导入按钮'
        for toolbar_info in dict_conf["toolbar"]:
            self.make_bar(toolbar_info)

    def make_bar(self, dict_info):
        toolbar = QToolBar(dict_info["name"], self.parent)
        for dict_member in dict_info["members"]:
            add_action(toolbar, dict_member)
        self.list_bars.append(toolbar)
