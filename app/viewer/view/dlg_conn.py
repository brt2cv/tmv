from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox
from utils.uic import loadUi

from utils.log import getLogger
logger = getLogger()

class DlgUdpConnect(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        loadUi("ui/dlg_conn.ui", self)
        self.setWindowTitle("UDP连接配置")

        self._setup_ui()
        self._activate()

    def _setup_ui(self):
        from PyQt5.QtWidgets import QRadioButton, QButtonGroup

        self.btn_group = QButtonGroup(self)
        list_choices = ["localhost", "中转服务器"]
        for index, choice in enumerate(list_choices):
            btn_radio = QRadioButton(choice, self)
            self.btn_group.addButton(btn_radio, index)
            self.ly_choices.addWidget(btn_radio)

    def _activate(self):
        self.btn_group.buttonClicked.connect(self.on_radio_clicked)

    def on_radio_clicked(self, wx_radio):
        id_ = self.btn_group.checkedId()
        # index = list_choices.index(wx_radio.text())

        if id_ == 0:
            self.ed_addr.setText("127.0.0.1")
        elif id_ == 1:
            # 加载全局设置
            from ..setting import PluginSettings
            setting = PluginSettings()

            ipaddr=setting.get("broker", "ipaddr")
            self.ed_addr.setText(ipaddr)

    # def closeEvent(self, event):
    #     QMessageBox.warning(self, "警告", "无法连接到服务器")
    #     return super.closeEvent(event)
