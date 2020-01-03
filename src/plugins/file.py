from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from utils.qt5 import dialog_file_select

import mvlib.io
import mvlib.transform

import core
from core.plugin.filter import Filter, DialogFilter


class OpenImageFile(Filter):
    scripts = "{output} = mvlib.io.imread({path_img})"

    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(core.g.get("mwnd"), "Images (*.png *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            QMessageBox.warning(core.g.get("mwnd"), "错误", "请勿选择多张图片")
            return
        path_pic = file_path[0]
        self.open(path_pic)

    def open(self, path_pic):
        self.para["path_img"] = f"\"{path_pic}\""  # commit scripts para

        self.set_image(mvlib.io.imread(path_pic))
        core.g.call("prompt", f"载入图像：{path_pic}", 5)


class SaveAsImageFile(Filter):
    scripts = "{output} = mvlib.io.imwrite({path_img}, {im})"

    def run(self):
        file_name, str_filter = QFileDialog.getSaveFileName(
                                core.g.get("mwnd"),
                                "图像另存为",
                                filter="Images (*.jpg *.png)")
        if file_name:
            ips = self.get_image()
            mvlib.io.imwrite(file_name, ips)
            core.g.call("prompt", f"图像已存储至：{file_name}", 5)


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
    scripts = "{output} = mvlib.transform.resize({im}, {size})"

    def processing(self, im_arr):
        width = int(self.para["width"])
        height = int(self.para["height"])
        self.para["size"] = [width, height]  # commit scripts para
        return mvlib.transform.resize(im_arr, self.para["size"])

    def run(self):
        ips = self.get_image()
        w, h = ips.shape[:2]
        self.view[0]["val_init"] = w
        self.view[1]["val_init"] = h
        super().run()
