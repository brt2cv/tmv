from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QByteArray, QDataStream, QMimeData, QIODevice, QSize, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QDrag


import traceback
def dump_exception(e):
    print("%s EXCEPTION:" % e.__class__.__name__, e)
    traceback.print_tb(e.__traceback__)


class DragListWidget(QListWidget):
    icon_size = 32

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        from PyQt5.QtWidgets import QAbstractItemView

        self.setIconSize(QSize(self.icon_size, self.icon_size))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

    def make_item(self, dict_info):
        item = QListWidgetItem(dict_info["name"], self)
        pixmap = QPixmap(dict_info.get("icon"))
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(self.icon_size, self.icon_size))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # # setup data
        # item.setData(Qt.UserRole, pixmap)

        # op_code=0
        # item.setData(Qt.UserRole + 1, op_code)

    def startDrag(self, *args, **kwargs):
        LISTBOX_MIMETYPE = "application/x-item"
        # try:
        item = self.currentItem()
        op_code = item.data(Qt.UserRole + 1)

        pixmap = QPixmap(item.data(Qt.UserRole))
        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap
        dataStream.writeInt(op_code)
        dataStream.writeQString(item.text())

        mimeData = QMimeData()
        mimeData.setData(LISTBOX_MIMETYPE, itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
        drag.setPixmap(pixmap)

        drag.exec_(Qt.MoveAction)

        # except Exception as e:
        #     dump_exception(e)
