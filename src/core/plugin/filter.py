from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
from PyQt5.QtCore import Qt
from .. import g
from .features import IpsFeature, FeatureTypeError
from . import Plugin

from utils.log import getLogger
logger = getLogger()

class FilterBase(Plugin):
    """ 图像相关的插件基类 """
    features = {}

    def processing(self, im_arr):
        """ 处理图像 """

    def get_image(self):
        """ 获取需要处理的图像，需要子类实现 """
        im_arr = g.get("canvas").get_image()
        return im_arr

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        g.get("canvas").set_image(im_arr)

    def update_canvas(self):
        """ 刷新UI """
        g.get("canvas").update()

    def check_features(self, im_arr):
        """ if check error, raise FeatureTypeError """
        fts = IpsFeature(self.features)
        fts.check(im_arr)

    def run(self):
        im_arr = self.get_image()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        self.set_image(im2)


class Filter(FilterBase):
    """ 对于ImageContainer进行操作 """
    def get_image(self):
        im_mgr = g.get("canvas").get_container()
        ips = im_mgr.get_snap()
        return ips

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        im_mgr = g.get("canvas").get_container()
        im_mgr.commit(im_arr)
        self.update_canvas()

    def update_canvas(self):
        """ 刷新UI """
        g.get("canvas").repaint()


from functools import partial
from .widgets import TplWidgetsManager
class DialogFilterBase(QDialog, Filter):
    title = "Filter"
    view = []  # 简单的垂直布局
    # { "type": "slider",
    #   "val_range": [0, 100]
    #   ...
    #   "para": "thresh"
    # }

    def __init__(self, parent):
        """ parent为Qt的UI父类
            与父类的通讯，应由pyqtSignal负责，而非调用父类实例
        """
        super().__init__(parent)
        self.para = {}  # para_name: value
        self.needSetupUi = True

    def setup_ui(self):
        self.resize(400, 10)
        dlg_layout = QVBoxLayout(self)
        self.mlayout = QVBoxLayout()  # 主显示区
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        # self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # self.buttonBox.clicked.connect(self.on_btn_clicked)
        btn_ok = QPushButton("OK", self)
        btn_cancel = QPushButton("Cancel", self)
        self.buttonBox.addButton(btn_ok, QDialogButtonBox.YesRole)
        self.buttonBox.addButton(btn_cancel, QDialogButtonBox.NoRole)
        btn_ok.clicked.connect(self.accepted)
        btn_cancel.clicked.connect(self.rejected)

        dlg_layout.addLayout(self.mlayout)
        dlg_layout.addWidget(self.buttonBox)

        #####################################################################
        self.setWindowTitle(self.title)

        tpl_wx_mgr = TplWidgetsManager(self)
        for dict_wx in self.view:
            para_name = dict_wx["para"]
            para_val = dict_wx.get("val_init", 0)

            wx = tpl_wx_mgr.parse_elem(dict_wx)
            if "para" in dict_wx:
                self.para[para_name] = para_val

            wx.set_slot(partial(self.on_para_changed, para_name, wx))
            self.mlayout.addWidget(wx)

    # def on_btn_clicked(self, btn):
    #     try:
    #         role = self.buttonBox.standardButton(btn)
    #         if role == QDialogButtonBox.Ok:
    #             self.accepted()
    #         elif role == QDialogButtonBox.Cancel:
    #             self.rejected()
    #     except FeatureTypeError:
    #         return

    def on_para_changed(self, para_name, wx):
        self.para[para_name] = wx.get_value()

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        im_mgr = g.get("canvas").get_container()
        im_mgr.commit(im_arr)

    def reset(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.reset()
        self.update_canvas()

    def accepted(self):
        """ 将当前图像设置为image """
        try:
            im_arr = self.get_image()
            self.check_features(im_arr)

            im2 = self.processing(im_arr)
            self.set_image(im2)  # 更新snap
            self.update_canvas()

        except Exception as e:
            logger.warning(e)

    def rejected(self):
        """ 取消图像变更 """
        self.reset()

    def run(self):
        """ 调用的接口，显示主窗口 """
        if self.needSetupUi:
            self.setup_ui()  # 延迟构造窗口UI
            self.needSetupUi = False

        ips = self.get_image()
        self.check_features(ips)
        self.show()


class DialogFilter(DialogFilterBase):
    """ 增加预览功能 """
    def setup_ui(self):
        super().setup_ui()
        # 添加reset按钮
        btn_reset = QPushButton("Reset", self)
        btn_preview = QPushButton("Preview", self)
        self.buttonBox.addButton(btn_preview, QDialogButtonBox.ResetRole)
        self.buttonBox.addButton(btn_reset, QDialogButtonBox.ResetRole)
        btn_reset.clicked.connect(self.reset)
        btn_preview.clicked.connect(self.preview)

    def preview(self):
        try:
            im_arr = self.get_image()
            self.check_features(im_arr)

            im2 = self.processing(im_arr)
            im_mgr = g.get("canvas").get_container()
            im_mgr.set_image(im2)  # 不更新snap
            self.update_canvas()

        except Exception as e:
            logger.warning(e)

    # @override
    def on_para_changed(self, para_name, wx):
        super().on_para_changed(para_name, wx)
        self.preview()  # 实时预览

    def run(self):
        super().run()
        self.preview()  # 显示窗口时即应用预览
