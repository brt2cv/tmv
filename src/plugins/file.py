from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from utils.qt5 import dialog_file_select

from utils.imgio import imread, imwrite
from mvlib import resize

from core import g
from core.plugin.filter import Filter, DialogFilter

class NewViewerLabel(Filter):
    def run(self):
        """ override: 无需打开图像 """
        g.get("canvas").add_tab_stack()


class OpenImageFile(Filter):
    scripts = "{output} = mvlib.io.imread({path_img})"

    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(g.get("mwnd"), "Images (*.png *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            QMessageBox.warning(g.get("mwnd"), "错误", "请勿选择多张图片")
            return
        path_pic = file_path[0]
        self.open(path_pic)

    def open(self, path_pic):
        self.para["path_img"] = f"\"{path_pic}\""  # commit scripts para

        self.set_image(imread(path_pic))
        g.call("prompt", f"载入图像：{path_pic}", 5)


class SaveAsImageFile(Filter):
    def run(self):
        file_name, str_filter = QFileDialog.getSaveFileName(
                                g.get("mwnd"),
                                "图像另存为",
                                filter="Images (*.jpg *.png)")
        if file_name:
            ips = self.get_image()
            imwrite(file_name, ips)
            g.call("prompt", f"图像已存储至：{file_name}", 5)


class ResizeImageFile(DialogFilter):
    title = "Resize Image"
    view = [{
        "type": "edit",
        "name": "width  ",
        "isCheckbox": False,
        "para": "width"
    },{
        "type": "edit",
        "name": "height ",
        "isCheckbox": False,
        "para": "height"
    }]
    scripts = "{output} = mvlib.resize({im}, {size})"

    def processing(self, im_arr):
        width = int(self.para["width"])
        height = int(self.para["height"])
        self.para["size"] = [width, height]  # commit scripts para
        return resize(im_arr, self.para["size"])

    def run(self):
        ips = self.get_image()
        w, h = ips.shape[:2]
        self.view[0]["val_init"] = w
        self.view[1]["val_init"] = h
        super().run()

class AboutMe(Filter):
    def run(self):
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             "关于",
                             "感谢ImagePy的开源，回馈开源社区",
                             parent = g.get("mwnd"))
        msgbox.setDetailedText('版权：Bright Li\nTel: 18131218231\nE-mail: brt2@qq.com')
        msgbox.setIconPixmap(QPixmap("app/mvtool/res/logo.png"))
        msgbox.exec_()
