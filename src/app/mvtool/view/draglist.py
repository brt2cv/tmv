from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QByteArray, QDataStream, QMimeData, QIODevice, QSize, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QDrag


class DragListWidget(QListWidget):
    icon_size = 32
    mime_type = "application/x-item"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        from PyQt5.QtWidgets import QAbstractItemView

        self.setIconSize(QSize(self.icon_size, self.icon_size))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

    # def addItem(self, str_item):
    #     super().addItem(str_item)

    def make_item(self, dict_info):
        item = QListWidgetItem(dict_info["name"], self)
        pixmap = QPixmap(dict_info.get("icon"))
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(self.icon_size, self.icon_size))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole+1, dict_info["plugin"])

    def startDrag(self, *args, **kwargs):
        item = self.currentItem()

        # 拖动时鼠标前端显示对象pixmap
        pixmap = QPixmap(item.data(Qt.UserRole))
        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap

        # op_code = item.data(Qt.UserRole + 1)
        # dataStream.writeInt(op_code)
        # dataStream.writeQString(item.text())

        mimeData = QMimeData()
        mimeData.setData(self.mime_type, itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)  # 设置数据
        drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
        drag.setPixmap(pixmap)

        drag.exec_(Qt.MoveAction)


from utils.base import rpath2curr
path_conf = rpath2curr("./draglist.json")

from PyQt5.QtWidgets import QToolBox
class ListBoxCreator:
    def __init__(self, parent):
        import json
        # self.parent = parent
        with open(path_conf, "r", encoding='utf8') as fp:
            dict_conf = json.load(fp)

        top_box = QToolBox(parent)
        for menu_group_info in dict_conf["draglist"]:
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
        unit_list = DragListWidget(parent_box)
        for dict_member in dict_group["members"]:
            if "members" in dict_member:
                # box = QToolBox(self.parent)
                # self.make_unit(box, dict_member)
                # unit_list.addItem(box)
                assert True, f"目前尚不支持超过2级菜单的结构"
                # unit_list.addItem(dict_member["name"])

            else:
                unit_list.make_item(dict_member)

        parent_box.addItem(unit_list, dict_group["name"])
