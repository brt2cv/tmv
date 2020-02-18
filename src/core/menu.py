# 罗列了关于menu.json解析相关类
try:
    import json5 as json
except ImportError:
    import json

from utils.qt5 import make_action, make_submenu
from core.plugin.mgr import PluginManager

from core import getLogger
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


from PyQt5.QtWidgets import QToolBox
class ListBoxCreator:
    def __init__(self, parent, path_conf):
        self.parent = parent

        with open(path_conf, "r", encoding='utf8') as fp:
            dict_conf = json.load(fp)

        plug_list = "draglist" if "draglist" in dict_conf else "menubar"
        top_box = QToolBox(self.parent)
        for menu_group_info in dict_conf[plug_list]:
            self.make_unit(top_box, menu_group_info)
        self.listbox = top_box

    def widget(self):
        return self.listbox

    # def make_label(self, parent_listbox, dict_info):
    #     if "members" in dict_info:
    #         node_name = dict_info["name"]
    #         submenu = make_submenu(parent_menu, node_name)
    #         # 展开submenu
    #         for elem in dict_info["members"]:  # 递归
    #             self.make_label(parent_listbox, elem)
    #     else:
    #         parent_listbox.make_item(dict_info)

    def make_unit(self, parent_box, dict_group):
        """ parent_box: a QToolBox widget """
        from .draglist import DragListWidget

        unit_list = DragListWidget(parent_box)
        for dict_member in dict_group["members"]:
            if "members" in dict_member:
                # box = QToolBox(self.parent)
                # self.make_unit(box, dict_member)
                # unit_list.addItem(box)
                assert True, f"目前尚不支持超过2级菜单的结构"
                unit_list.addItem(dict_member["name"])

            else:
                unit_list.make_item(dict_member)

        parent_box.addItem(unit_list, dict_group["name"])


from PyQt5.QtWidgets import QToolBar
from PyQt5.QtCore import QSize

icon_size = -1
def _get_iconsize():
    """ 运行时加载 """
    global icon_size

    from core import conf_mgr
    icon_size = conf_mgr.get("app", "gui", "icon_size")
    icon_size = int(icon_size) if icon_size else None

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

        if icon_size == -1:
            _get_iconsize()
        if icon_size:
            toolbar.setIconSize(QSize(icon_size, icon_size))
        # toolbar.setFixedHeight(36)
        self.list_bars.append(toolbar)
