from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from .. import g, ImagePlus
from .features import IpsFeature, FeatureTypeError


class Plugin:
    def run(self):
        """ Plugin的运行函数 """


class Plugin4ImgProcessing(Plugin):
    features = {}

    def processing(self, ips):
        """ 处理图像 """

    def get_image(self):
        """ 获取需要处理的图像，需要子类实现 """
        im_curr = g.get("canvas").get_image()
        return im_curr

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        g.get("canvas").set_image(im_arr)

    def check_features(self, ips):
        """ if check error, raise FeatureTypeError """
        fts = IpsFeature(self.features)
        fts.check(ips)

    def run(self):
        ips = self.get_image()
        self.check_features(ips)

        im2 = self.processing(ips)
        ips2 = ImagePlus(im2, ips.meta)
        self.set_image(ips2)


class DialogPlugin(QDialog, Plugin4ImgProcessing):
    # def __init__(self, parent, attach=None):
    #     """ parent为逻辑上的父类，成员变量可能需要调用parent中的member/method
    #         attach为Qt的UI父类。
    #     """
    #     super().__init__(parent if attach is None else attach)

    def __init__(self, parent):
        """ parent为Qt的UI父类
            与父类的通讯，应由pyqtSignal负责，而非调用父类实例
        """
        from util.qt5 import loadUi

        super().__init__(parent)
        loadUi("template/base.ui", self)
        self.buttonBox.clicked.connect(self.on_btn_clicked)

    # def make_dialog(self, parent):
    #     # 延迟构造...
    #     from util.gmgr import g
    #     dlg = DlgTplBase(g.get("mwnd"))
    #     return dlg

    def batch(self):
        super().run()

    def on_btn_clicked(self, btn):
        try:
            role = self.buttonBox.standardButton(btn)
            if role == QDialogButtonBox.Ok:
                self.accepted()
            elif role == QDialogButtonBox.Cancel:
                self.rejected()
            else:  # Reset
                self.batch()
        except FeatureTypeError:
            return

    def accepted(self):
        """ 将当前图像设置为image """
        self.batch()
        ips = self.get_image()
        ips.take_snap()

    def rejected(self):
        """ 取消图像 """
        ips = self.get_image()
        ips2 = ips.reset()
        self.set_image(ips2)

    def run(self):
        """ 调用的接口，显示主窗口 """
        ips = self.get_image()
        self.check_features(ips)
        self.show()
