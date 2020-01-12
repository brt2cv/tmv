import mvlib
from utils.imgio import pillow2ndarray
from core import g, alert, conf_mgr
from core.plugin.filter import Filter, DialogFilter

scaling = None  # False if not compress
def _read_scaling():
    global scaling
    if conf_mgr.get("app", "img", "compress") == "true":
        scaling = int(conf_mgr.get("app", "img", "scaling_min_pixel"))
    else:
        scaling = False

def _auto_scaling(im_arr, isPillow):
    """ 自动压缩图像 """
    if scaling is None:
        _read_scaling()
    if scaling:
        h, w = im_arr.size if isPillow else im_arr.shape[:2]
        min_ = min(h, w)
        if min_ > scaling:  # 触发压缩
            r = int(min_ / scaling) +1
            h_, w_ = int(h/r), int(w/r)
            im_arr = mvlib.transform.resize(im_arr, (h_, w_))
    return im_arr


from utils.qt5 import dialog_file_select
class OpenImageFile(Filter):
    scripts = "{output} = mvlib.io.imread({path_img})"

    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(g.get("mwnd"), "Images (*.png *.jpg)")
        if not file_path:
            return
        # elif len(file_path) > 1:
        #     alert(g.get("mwnd"), "错误", "请勿选择多张图片")
        #     return
        path_pic = file_path[0]
        self.open(path_pic)

    def open(self, path_pic):
        self.paras["path_img"] = f"\"{path_pic}\""  # commit scripts para
        im_arr = mvlib.io.imread(path_pic)

        isPillow = mvlib.get_backend() == "pillow"

        # 自动压缩图像
        im_arr = _auto_scaling(im_arr, isPillow)
        if isPillow:
            im_arr = pillow2ndarray(im_arr)
        self.set_image(im_arr)
        g.call("prompt", f"载入图像：{path_pic}", 5)
        return im_arr


import os.path
class OpenImageFolder(Filter):
    def run(self):
        from glob import glob
        dir_imgs = dialog_file_select(g.get("mwnd"), onlyDir=True)
        if not dir_imgs:
            return
        list_files = glob(os.path.join(dir_imgs[0], "*.jpg"))
        if not list_files:
            alert("空文件夹，未筛选到【jpg】图像")
            return
        g.register("list_files", list_files, forced=True)
        self.open_first(list_files)

    def open_first(self, list_files):
        path_pic = list_files[0]
        im_arr = mvlib.io.imread(path_pic)
        im_arr = _auto_scaling(im_arr, False)
        self.set_image(im_arr)
        g.call("prompt", f"载入图像：{path_pic}", 5)
        g.register("curr_file", 0, forced=True)
        return im_arr, path_pic


class FolderImageNext(Filter):
    def run(self):
        list_files = g.get("list_files")
        if not list_files:
            alert("尚未选择目标文件夹")
            return
        curr_idx = g.get("curr_file") + 1
        if curr_idx >= len(list_files):
            alert("已浏览至最后一张图像")
            return
        self.open(list_files, curr_idx)

    def open(self, list_files, index):
        path_pic = list_files[index]
        im_arr = mvlib.io.imread(path_pic)
        im_arr = _auto_scaling(im_arr, False)
        self.set_image(im_arr)
        g.call("prompt", f"载入图像：{path_pic}", 5)
        g.override("curr_file", index)
        return im_arr, path_pic


class FolderImageLast(Filter):
    def run(self):
        list_files = g.get("list_files")
        if not list_files:
            alert("尚未选择目标文件夹")
            return
        curr_idx = g.get("curr_file")
        if curr_idx <= 0:
            alert("已浏览至第一张图像")
            return
        self.open(list_files, curr_idx-1)

    def open(self, list_files, index):
        path_pic = list_files[index]
        im_arr = mvlib.io.imread(path_pic)
        self.set_image(im_arr)
        g.call("prompt", f"载入图像：{path_pic}", 5)
        g.override("curr_file", index)
        return im_arr, path_pic


import utils  # 视图窗口图像以ndarray存储，保存时pillow后端无法执行save操作
from PyQt5.QtWidgets import QFileDialog
class SaveAsImageFile(Filter):
    scripts = "{output} = utils.imgio.imwrite({path_img}, {im})"

    def run(self):
        file_name, str_filter = QFileDialog.getSaveFileName(
                                g.get("mwnd"),
                                "图像另存为",
                                filter="Images (*.jpg *.png)")
        if file_name:
            ips = self.get_image()
            utils.imgio.imwrite(file_name, ips)
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
