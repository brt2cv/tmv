from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from utils.uic import loadUi
from utils.qt5wx.wx_unit import UnitSlider

from ..grab.grabbase import IImageGrabber
from ..grab.ip_grabber import *

from utils.log import getLogger
logger = getLogger()

from ..setting import PluginSettings
setting = PluginSettings()
IMG_GRAB_PORT = int(setting.get("broker", "port"))

STATUS_INFO_TIME = 5000

class UnitViewer(QWidget):
    connStatChanged = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        loadUi("ui/wx_viewer.ui", self)
        self.setProperty("class", "bkg")  # for qss

        self._setup()
        self._setup_ui()
        self._activate()

    def _setup(self):
        self.grabber = None  # IImageGrabber()
        self.grabber_type = None
        self.isPause = False
        self.upload_client = None

    def _setup_ui(self):
        from PyQt5.QtWidgets import QToolBar, QAction
        from PyQt5.QtGui import QIcon

        toolbar = QToolBar("Default", self)

        conn_hid = QAction(QIcon("plugin/viewer/res/USB.png"), "访问本地HID数据", self)
        conn_udp = QAction(QIcon("plugin/viewer/res/Connect-Established.png"), "访问UDP数据", self)
        conn_tcp = QAction(QIcon("plugin/viewer/res/DB-Commit.png"), "访问远程服务器数据", self)
        conn_pause = QAction(QIcon("plugin/viewer/res/pause.png"), "暂停数据传输", self)
        conn_stop = QAction(QIcon("plugin/viewer/res/Exit.png"), "断开数据连接", self)

        toolbar.addAction(conn_hid)
        toolbar.addAction(conn_udp)
        toolbar.addAction(conn_tcp)
        toolbar.addAction(conn_pause)
        toolbar.addAction(conn_stop)
        self.ly_header.addWidget(toolbar)

        # activate:
        conn_udp.triggered.connect(self.conn_to_local)
        conn_tcp.triggered.connect(self.conn_to_broker)
        conn_hid.triggered.connect(self.conn_to_hid)
        conn_pause.triggered.connect(self.conn_pause)
        conn_stop.triggered.connect(self.conn_stop)

        from PyQt5.QtWidgets import QStatusBar
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("欢迎访问viewer")
        self.ly_footer.addWidget(self.status_bar)

        # # Ctrl-Zone:
        # from PyQt5.QtWidgets import QFrame, QVBoxLayout
        # frame = QFrame(self)
        # layout = QVBoxLayout()
        # frame.setLayout(layout)

        # Exposure = UnitSlider(frame, "传感器曝光", 0, val_range=[0, 255], isCheckbox=False)
        # Gain = UnitSlider(frame, "传感器增益", 0, val_range=[0, 255], isCheckbox=False)
        # layout.addWidget(Exposure)
        # layout.addWidget(Gain)

        # # 由于'IImageGrabber'没有hid_io, 故嵌套一层看似无意义的lambda
        # Exposure.set_slot(lambda x: self.grabber.hid_io.set_exposure(x))
        # Gain.set_slot(lambda x: self.grabber.hid_io.set_gain(x))
        # self.ly_ctrl.addWidget(frame)

        # self.frm_ctrl = frame
        # self.activate_ctrl_zone(False)

    def activate_ctrl_zone(self, value):
        # self.frm_ctrl.setEnabled(value)
        pass

    def setup_canvas(self, canvas_area=None):
        if canvas_area is None:
            from core.ui.scroll_canvas import ImageScrollCanvas
            self.canvas = ImageScrollCanvas(self)
        else:
            self.canvas = canvas_area
        self.ly_show.addWidget(self.canvas)

    def _activate(self):
        pass

    def closeEvent(self, e):
        self.conn_stop()
        return super().closeEvent(e)

    def conn_to_hid(self):
        if self.grabber_type == "hid":
            # self.status_bar.showMessage("", STATUS_INFO_TIME)
            QMessageBox.information(self, "提示", "当前已连接到HID设备")
            return
        elif self.grabber_type != None:
            QMessageBox.warning(self, "警告", "请先关闭当前连接")
            return

        # 询问是否上传服务器
        reply = QMessageBox.question(self, "警告", "是否将图像上传服务器？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ipaddr = setting.get("broker", "ipaddr")
            upload_clnt = BrokerRequestGrabber(ipaddr, IMG_GRAB_PORT)
            upload_clnt.listen()
            self.upload_client = upload_clnt

        self._conn_to_hid()
        self.activate_ctrl_zone(True)
        self.status_bar.showMessage("连接HID设备成功", STATUS_INFO_TIME)

    def _conn_to_hid(self):
        from ..grab.hid_grabber import HidGrabber
        self.grabber = HidGrabber()
        self.grabber_type = "hid"

        self.grabber.dataUpdated.connect(self.update_frame)
        self.grabber.listen()
        self.connStatChanged.emit(True)

    def conn_to_broker(self):
        if self.grabber_type == "broker":
            # self.status_bar.showMessage("", STATUS_INFO_TIME)
            QMessageBox.information(self, "提示", "当前已连接到远程计算机")
            return
        elif self.grabber_type != None:
            QMessageBox.warning(self, "警告", "请先关闭当前连接")
            return

        # 连接broker取图
        ipaddr = setting.get("broker", "ipaddr")
        self.grabber = BrokerReplyGrabber(ipaddr, IMG_GRAB_PORT)
        self.grabber_type = "broker"
        self.grabber.dataUpdated.connect(self.update_frame)
        self.grabber.reglistRecv.connect(self.sync_dialog)

        def msgbox_break():
            information = "远端已关闭连接（或者网络信号断开），如需再次申请协助，请重启连接"
            QMessageBox.warning(self, "警告", information)
            self.conn_stop()

        self.grabber.routine.protocal.connBreak.connect(msgbox_break)
        self.grabber.listen()

    def sync_dialog(self, dict_reglist):
        """ 异步并非最佳方案——需要支持同步 """
        def close_and_return():
            self.grabber.stop()
            self._setup()
            self.status_bar.showMessage("未连接到任何服务", STATUS_INFO_TIME)

        from .dlg_requests import DlgRequestList
        dlg_list = DlgRequestList(self, dict_reglist)
        ok = dlg_list.exec()
        if not ok:
            close_and_return()
            return

        conn_to = dlg_list.ed_addr.text()
        if not conn_to:  # 未选择
            close_and_return()
            return
        # conn_to = "191313012212614"

        self.grabber.connect(conn_to)

        self.connStatChanged.emit(True)
        self.status_bar.showMessage("已连接到远程计算机", STATUS_INFO_TIME)

    def conn_to_local(self):
        if self.grabber_type == "local":
            # self.status_bar.showMessage("", STATUS_INFO_TIME)
            QMessageBox.information(self, "提示", "当前已连接到UDP")
            return
        elif self.grabber_type != None:
            QMessageBox.warning(self, "警告", "请先关闭当前连接")
            return

        from .dlg_conn import DlgUdpConnect
        dlg_conn = DlgUdpConnect(self)
        ok = dlg_conn.exec()
        if not ok:
            return

        # 连接udp取图
        self.grabber = LocalGrabber()

        ipaddr = dlg_conn.ed_addr.text()
        if ipaddr == "127.0.0.1":
            # 本地做服务端
            self.grabber.setup_server(IMG_GRAB_PORT)

        else:
            # 本地做客户端
            self.grabber.setup_client(ipaddr, IMG_GRAB_PORT)

        self.grabber_type = "local"
        self.grabber.dataUpdated.connect(self.update_frame)
        self.grabber.listen()

        self.connStatChanged.emit(True)
        self.status_bar.showMessage("UDP已连接", STATUS_INFO_TIME)

    def conn_pause(self, **kwargs):
        if not self.grabber_type:
            return

        if "value" in kwargs:
            self.isPause = kwargs["value"]
        else:
            self.isPause = not self.isPause
        self.grabber.pause(self.isPause)

        if self.isPause:
            self.status_bar.showMessage("已暂停取图")
        else:
            self.status_bar.showMessage("已恢复取图", STATUS_INFO_TIME)

    def conn_stop(self):
        if not self.grabber_type:
            return
        self.grabber.stop()

        if self.upload_client:
            self.upload_client.stop()
        self._setup()

        self.connStatChanged.emit(False)
        if self.grabber_type == "hid":
            self.activate_ctrl_zone(False)
        self.status_bar.showMessage("已断开连接")

    def update_frame(self, im_array):
        self.canvas.set_ndarray(im_array)
        if self.upload_client:
            try:
                self.upload_client.routine.protocal.send_image(im_array)
            except OSError:
                self.upload_client.stop()
                self.upload_client = None

                information = "远程协助端已关闭连接，如需再次申请协助，请关闭当前连接后，重启HID数据连接"
                QMessageBox.warning(self, "警告", information)
