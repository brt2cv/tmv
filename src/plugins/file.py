import mvlib
from core import g, alert
from core.plugin.filter import Filter, DialogFilter


from utils.qt5 import dialog_file_select
class OpenImageFile(Filter):
    scripts = "{output} = mvlib.io.imread({path_img})"

    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(g.get("mwnd"), "Images (*.png *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            alert(g.get("mwnd"), "错误", "请勿选择多张图片")
            return
        path_pic = file_path[0]
        self.open(path_pic)

    def open(self, path_pic):
        self.paras["path_img"] = f"\"{path_pic}\""  # commit scripts para

        self.set_image(mvlib.io.imread(path_pic))
        g.call("prompt", f"载入图像：{path_pic}", 5)


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
        width = int(self.paras["width"])
        height = int(self.paras["height"])
        self.paras["size"] = [width, height]  # commit scripts para
        return mvlib.transform.resize(im_arr, self.paras["size"])

    def run(self):
        ips = self.get_image()
        w, h = ips.shape[:2]
        self.view[0]["val_init"] = w
        self.view[1]["val_init"] = h
        super().run()


from core.imgio import ImgIOManager
class RcpImageSwitch(Filter):
    def __init__(self):
        super().__init__()
        self.imgio_mgr = ImgIOManager()
        self.status = False  # 默认关闭状态

    def run(self):
        # self.status = not self.status
        if not self.status:
            self.imgio_mgr.rcp_start()
            self.status = True
        else:
            # self.imgio_mgr.rcp_stop()
            self.imgio_mgr.rcp_pause()

class RcpImagePause(Filter):
    def run(self):
        ImgIOManager().rcp_pause()
