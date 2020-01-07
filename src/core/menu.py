# 罗列了关于menu.json解析相关类
try:
    import json5 as json
except ImportError:
    import json

from utils.qt5 import make_action, make_submenu
from core.plugin.mgr import PluginManager

from utils.log import getLogger
logger = getLogger()
plug_mgr = PluginManager()


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
        # self.dict_menu = {self.menubar: {}}
        with open(path_conf, "r", encoding='utf8') as fp:
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


from PyQt5.QtWidgets import QToolBar
class ToolbarCreator:
    def __init__(self, parent):
        self.parent = parent
        self.list_bars = []

    def load_conf(self, path_conf):
        with open(path_conf, "r", encoding='utf8') as fp:
            dict_conf = json.load(fp)
        assert "toolbar" in dict_conf, '格式错误，未发现【"toolbar"】项，无法导入按钮'
        for toolbar_info in dict_conf["toolbar"]:
            self.make_bar(toolbar_info)

    def make_bar(self, dict_info):
        toolbar = QToolBar(dict_info["name"], self.parent)
        for dict_member in dict_info["members"]:
            add_action(toolbar, dict_member)
        self.list_bars.append(toolbar)
