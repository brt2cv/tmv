from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from .. import g
from .features import IpsFeature, FeatureTypeError
from . import Plugin

class FilterBase(Plugin):  # Plugin4ImgProcessing
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
        im_arr = im_mgr.get_snap()
        return im_arr

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        im_mgr = g.get("canvas").get_container()
        im_mgr.commit(im_arr)
        self.update_canvas()

    def update_canvas(self):
        """ 刷新UI """
        g.get("canvas").canvas.update()


from .widgets import TplWidgetsManager
class DialogFilter(QDialog, Filter):
    title = "Filter"
    view = []  # 简单的垂直布局
    # { "type": "slider",
    #   "val_range": [0, 100]
    #   ...
    #   "para4": "thresh"
    # }

    def __init__(self, parent):
        """ parent为Qt的UI父类
            与父类的通讯，应由pyqtSignal负责，而非调用父类实例
        """
        super().__init__(parent)
        self.para = {}  # para_name: wx_elem
        self.setup_ui()

    # def _declare(self):
    #     self.im_mgr
    #     self.im_arr

    def setup_ui(self):
        from util.qt5 import loadUi

        loadUi("template/base.ui", self)
        self.setWindowTitle(self.title)

        tpl_wx_mgr = TplWidgetsManager(self)
        for dict_wx in self.view:
            wx = tpl_wx_mgr.parse_elem(dict_wx)
            if "para" in dict_wx:
                self.para[dict_wx["para"]] = wx
            wx.set_slot(self.preview)  # 实时预览
            self.mlayout.addWidget(wx)

        self.buttonBox.clicked.connect(self.on_btn_clicked)

    def get_para(self, para_name):
        wx = self.para[para_name]
        value = wx.get_value()
        return value

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        im_mgr = g.get("canvas").get_container()
        im_mgr.commit(im_arr)

    # def make_dialog(self, parent):
    #     # 延迟构造...
    #     from util.gmgr import g
    #     dlg = DlgTplBase(g.get("mwnd"))
    #     return dlg

    def on_btn_clicked(self, btn):
        try:
            role = self.buttonBox.standardButton(btn)
            if role == QDialogButtonBox.Ok:
                self.accepted()
            elif role == QDialogButtonBox.Cancel:
                self.rejected()
            else:  # Reset
                self.reset()
        except FeatureTypeError:
            return

    def preview(self):
        im_arr = self.get_image()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        im_mgr = g.get("canvas").get_container()
        im_mgr.set_image(im2)  # 不更新snap
        self.update_canvas()

    def reset(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.reset()
        self.update_canvas()

    def accepted(self):
        """ 将当前图像设置为image """
        im_arr = self.get_image()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        self.set_image(im2)  # 更新snap
        self.update_canvas()

    def rejected(self):
        """ 取消图像变更 """
        self.reset()

    def run(self):
        """ 调用的接口，显示主窗口 """
        ips = self.get_image()
        self.check_features(ips)
        self.show()
        self.preview()  # 显示窗口时即应用预览
