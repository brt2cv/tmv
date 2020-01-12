from utils.base import singleton
import mvlib.io
from .plugin.filter import Filter

from core import getLogger
logger = getLogger()


@singleton
class ImgIOManager():
    def __init__(self):
        self.tid_rcp = None
        self.plugin = Filter()  # 支持Undo功能

    def open_file(self, path_file):
        im_arr = mvlib.io.imread(path_file)
        self.plugin.scripts = f"{{output}} = mvlib.io.imread(\"{path_file}\")"
        self.plugin.set_image(im_arr)

    def save_file(self, path_file, im_arr):
        mvlib.io.imwrite(path_file, im_arr)

    def rcp_start(self):
        """ 接收远程传输的图像 """
        from .rcp import make_server

        self.tid_rcp = make_server(byTcp=False)
        self.tid_rcp_pause = True
        self.rcp_pause()

    def rcp_recv(self, im_arr):
        logger.debug(f"接收到RCP图像, shape={im_arr.shape}")
        self.plugin.set_image(im_arr)

    def rcp_send(self):
        im_arr = self.plugin.get_image()
        self.tid_rcp.protocal.send_image(im_arr)

    def rcp_pause(self):
        if self.tid_rcp_pause:
            self.tid_rcp.protocal.dataUpdated.connect(self.rcp_recv)
        else:
            self.tid_rcp.protocal.dataUpdated.disconnect()
        self.tid_rcp_pause = not self.tid_rcp_pause

    def rcp_stop(self):
        if self.tid_rcp:
            self.tid_rcp.stop()
            logger.info("已关闭RCP服务")
