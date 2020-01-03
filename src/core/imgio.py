from utils.base import singleton
import mvlib.io
from . import g, alert

from utils.log import getLogger
logger = getLogger()


@singleton
class ImgIOManager():
    def __init__(self):
        self.plugin_open_file = OpenImageFile()

    def open_file(self, path_file):
        # im_arr = mvlib.io.imread(path_file)
        # g.get("canvas").set_image(im_arr)

        # 使用插件方式，支持UndoStock（但core模块依赖了plugins，合理吗？）
        self.plugin_open_file.open(path_file)

    def save_file(self, path_file, im_arr):
        mvlib.io.imwrite(path_file, im_arr)

    def rcp_open(self):
        """ 接收远程传输的图像 """
        from .rcp import make_server

        self.tid_rcp = make_server(byTcp=False)
        self.tid_rcp_pause = True
        self.on_rcp_pause()

    def rcp_recv(self, im_arr):
        logger.debug(f"接收到RCP图像, shape={im_arr.shape}")
        g.get("canvas").set_image(im_arr)

    def rcp_send(self, im_arr):
        g.get("canvas").get_image(im_arr)
        self.tid_rcp.protocal.send_image(im_arr)

    def on_rcp_pause(self):
        if self.tid_rcp_pause:
            self.tid_rcp.protocal.dataUpdated.connect(self.rcp_recv)
        else:
            self.tid_rcp.protocal.dataUpdated.disconnect()
        self.tid_rcp_pause = not self.tid_rcp_pause

    def rcp_close(self):
        self.tid_rcp.stop()
        logger.debug("已关闭RCP服务")


from utils.qt5 import dialog_file_select
from .plugin.filter import Filter
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
        self.para["path_img"] = f"\"{path_pic}\""  # commit scripts para

        self.set_image(mvlib.io.imread(path_pic))
        g.call("prompt", f"载入图像：{path_pic}", 5)
