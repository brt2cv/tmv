from utils.base import singleton
import mvlib.io
from . import g

from utils.log import getLogger
logger = getLogger(1)

def instance():
    return ImgIOManager()

@singleton
class ImgIOManager():
    # def __init__(self):

    def open_file(self, path_file):
        im_arr = mvlib.io.imread(path_file)
        g.get("canvas").set_image(im_arr)

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
