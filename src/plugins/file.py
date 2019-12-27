from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from utils.qt5 import dialog_file_select

from utils.imgio import imread, imwrite
from mvlib import resize

from core import g
from core.plugin.filter import Filter, DialogFilter


class OpenImageFile(Filter):
    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(g.get("mwnd"), "Images (*.png *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            QMessageBox.warning(g.get("mwnd"), "错误", "请勿选择多张图片")
            return
        path_pic = file_path[0]
        # g.get("canvas").load_image(path_pic)
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
        "name": "width",
        "isCheckbox": False,
        "para": "width"
    },{
        "type": "edit",
        "name": "height",
        "isCheckbox": False,
        "para": "height"
    }]

    def processing(self, im_arr):
        width = self.para["width"]
        height = self.para["height"]
        return resize(im_arr, [width, height])

    def run(self):
        ips = self.get_image()
        w, h = ips.shape[:2]
        self.view[0]["val_init"] = w
        self.view[1]["val_init"] = h
        super().run()

class CurrImageInfo(Filter):
    def _print_info(self, im):
        print(im)

        list_info = []
        print("#"*60)
        list_info.append(f"Shape: 【{im.shape}】")
        list_info.append(f"Size:  【{im.size}】")
        list_info.append(f"Type:  【{im.dtype}】")
        str_info = "\n".join(list_info)
        print(str_info)
        print("#"*60)
        return str_info

    def run(self):
        print(">> canvas显示图像(curr)")
        im_mgr = g.get("canvas").get_container()
        str_info = self._print_info(im_mgr.curr)
        QMessageBox.information(g.get("mwnd"), "图像信息", str_info)

        print(">> canvas存储图像(snap)")
        self._print_info(im_mgr.snap)
