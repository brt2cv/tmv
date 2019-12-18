from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal
from .. import g, ImagePlus
from .features import IpsFeature, FeatureTypeError


class Plugin:
    def run(self):
        """ Plugin的运行函数 """


class Filter(Plugin):  # Plugin4ImgProcessing
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
        self.update_canvas()

    def update_canvas(self):
        """ 刷新UI """
        g.get("canvas").update()
        print("update canvas...")

    def check_features(self, im_arr):
        """ if check error, raise FeatureTypeError """
        fts = IpsFeature(self.features)
        fts.check(im_arr)

    def run(self):
        im_arr = self.get_image()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        self.set_image(im2)


# from core.mgr import ImageManager
class DialogFilter(QDialog, Filter):
    title = "Filter"

    def __init__(self, parent):
        """ parent为Qt的UI父类
            与父类的通讯，应由pyqtSignal负责，而非调用父类实例
        """
        super().__init__(parent)
        self.setup_ui()

    # def _declare(self):
    #     self.im_mgr
    #     self.im_arr

    def setup_ui(self):
        from util.qt5 import loadUi

        loadUi("template/base.ui", self)
        self.setWindowTitle(self.title)
        self.buttonBox.clicked.connect(self.on_btn_clicked)

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
                self.preview()
        except FeatureTypeError:
            return

    def get_image(self):
        im_mgr = g.get("canvas").get_container()
        im_arr = im_mgr.get_snap()
        return im_arr

    # def set_image(self, im_arr):
    #     """ 将处理完成的图像，更新到主界面 """

    def preview(self):
        im_arr = self.get_image()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        self.set_image(im2)
        self.update_canvas()

    def accepted(self):
        """ 将当前图像设置为image """
        im_mgr = g.get("canvas").get_container()
        im_arr = im_mgr.get_snap()
        self.check_features(im_arr)

        im2 = self.processing(im_arr)
        im_mgr.commit(im2)

    def rejected(self):
        """ 取消图像变更 """
        im_mgr = g.get("canvas").get_container()
        ips2 = im_mgr.reset()
        self.update_canvas()

    def run(self):
        """ 调用的接口，显示主窗口 """
        ips = self.get_image()
        self.check_features(ips)
        self.show()
