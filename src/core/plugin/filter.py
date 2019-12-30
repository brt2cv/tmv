from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
from PyQt5.QtCore import Qt
from .. import g
from .format import IpsFormat, FormatTypeError
from . import Plugin

from utils.log import getLogger
logger = getLogger()

class FilterBase(Plugin):
    """ 图像相关的插件基类 """
    formats = {}

    def __init__(self):
        self._fmt_checker = IpsFormat(self.formats)

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

    def check_format(self, im_arr=None):
        """ if check error, raise False """
        if im_arr is None:
            im_arr = self.get_image()
        try:
            self._fmt_checker.check(im_arr)
        except FormatTypeError:
            return False
        else:
            return True

    def run(self):
        """ 集成流程 """
        im_arr = self.get_image()
        if self.check_format(im_arr):
            im2 = self.processing(im_arr)
            self.set_image(im2)


import re
class Filter(FilterBase):
    """ 对于ImageContainer进行操作 """
    scripts = ""  # or list of str
    para = {}
    _pattern = re.compile(r'{.+?}')

    def parse_script(self):
        """ 输入脚本，可多次调用，不断压入self.scripts中
            format:
                {img_out}, <var_out0>, var_out1 = <object>.operator(&, <var_in0>, var_in1)
                其中 img_in，即为当前curr_img；
                     img_out、object 通过UI获取；
                     var_out、var_in 可直接指定，也可能需要UI确定
            另，由于脚本会输出变量，需要增加变量名检测。
        """
        ret = self.scripts
        list_para = re.findall(self._pattern, self.scripts)
        for para_with_brace in list_para:
            para_name = para_with_brace[1:-1]
            if para_name in self.para:
                ret = ret.replace(para_with_brace, str(self.para[para_name]))
        return ret

    def get_image(self):
        im_mgr = g.get("canvas").get_container()
        ips = im_mgr.get_snap()
        return ips

    def set_image(self, im_arr):
        """ 将处理完成的图像，更新到主界面 """
        g.get("canvas").set_image(im_arr)
        im_mgr = g.get("canvas").get_container()
        script = self.parse_script()
        im_mgr.commit(script)
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
    #     except FormatTypeError:
    #         return

    def on_para_changed(self, para_name, wx):
        self.para[para_name] = wx.get_value()

    def reset(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.reset()
        self.update_canvas()

    def accepted(self):
        """ 将当前图像设置为image """
        im_arr = self.get_image()
        if self.check_format(im_arr):
            im2 = self.processing(im_arr)
            self.set_image(im2)  # 更新snap
            self.update_canvas()

    def rejected(self):
        """ 取消图像变更 """
        self.reset()

    def run(self):
        """ 调用的接口，显示主窗口 """
        if self.check_format():
            if self.needSetupUi:
                self.setup_ui()  # 延迟构造窗口UI
                self.needSetupUi = False
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
        im_arr = self.get_image()
        if self.check_format(im_arr):
            im2 = self.processing(im_arr)
            im_mgr = g.get("canvas").get_container()
            im_mgr.set_image(im2)  # 不更新snap
            self.update_canvas()

    # @override
    def on_para_changed(self, para_name, wx):
        super().on_para_changed(para_name, wx)
        self.preview()  # 实时预览

    def run(self):
        if self.check_format():
            if self.needSetupUi:
                self.setup_ui()  # 延迟构造窗口UI
                self.needSetupUi = False
            self.show()
            self.preview()  # 显示窗口时即应用预览
