import mvlib
from core import g
from core.plugin.filter import Filter, DialogFilter
from core.imgio import OpenImageFile, ImgIOManager


from PyQt5.QtWidgets import QFileDialog
class SaveAsImageFile(Filter):
    scripts = "{output} = mvlib.io.imwrite({path_img}, {im})"

    def run(self):
        file_name, str_filter = QFileDialog.getSaveFileName(
                                g.get("mwnd"),
                                "图像另存为",
                                filter="Images (*.jpg *.png)")
        if file_name:
            ips = self.get_image()
            mvlib.io.imwrite(file_name, ips)
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


class RcpImageSwitch(Filter):
    def __init__(self):
        super().__init__()
        self.imgio_mgr = ImgIOManager()
        self.status = True  # 默认是开启状态

    def run(self):
        self.status = not self.status
        if self.status:
            self.imgio_mgr.rcp_start()
        else:
            self.imgio_mgr.rcp_stop()


class RcpImagePause(Filter):
    def run(self):
        ImgIOManager().rcp_pause()
