from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox
from utils.uic import loadUi

from utils.log import getLogger
logger = getLogger()

class DlgRequestList(QDialog):
    def __init__(self, parent, dict_requests):
        super().__init__(parent)
        loadUi("ui/dlg_list.ui", self)
        self.setWindowTitle("UDP连接配置")

        self._setup_ui(dict_requests)
        self._activate()

    def _setup_ui(self, dict_requests):
        # dict_requests: {'123456': '127.0.0.1:53385'}
        for license, ipaddr in dict_requests.items():
            str_line = f"license: {license}  @{ipaddr}"
            self.listWidget.addItem(str_line)

    def _activate(self):
        self.listWidget.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, wx_item):
        # print(wx_item, type(wx_item))
        text = wx_item.text()
        text_strip = text.replace(" ", "")
        index_left = text_strip.find(":")
        index_right = text_strip.rfind("@")
        self.ed_addr.setText(text_strip[index_left +1 : index_right])
