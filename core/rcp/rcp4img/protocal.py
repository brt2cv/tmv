# encoding: utf-8

import numpy as np
from ..pub.trans import TransBase, json2dict

from util.imgio import bytes2ndarray, shape2size, shape2mode
from util.gmgr import g
from util.log import getLogger
logger = getLogger()

from PyQt5.QtCore import QObject, pyqtSignal
class RemoteImageQtTrans(TransBase, QObject):
    """ 文件传输协议
        向服务端发送文件：
    """
    dataUpdated = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

    ###########################################################################
    def reply(self, msg: bytes, sock1addr=None):
        # logger.debug("接收到消息：【{}】".format(msg))
        msg_head, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            # logger.debug("命令数据【{}】".format(msg))
            pass

        elif self.check_data(msg):
            # logger.debug("转发数据【{}】".format(msg))
            self.recv_image(msg_body, sock1addr)

        else:
            err = "Unkown request [{}]".format(msg)
            self.send_error(err.encode(), sock1addr)

    def parse_reply(self, msg: bytes):
        logger.debug("接收到回复：【{}】".format(msg))

    def send_image(self, im_array):
        """ 发送包结构：b'(640, 480, 3)|im_array' """
        shape = str(im_array.shape)
        data = shape.encode() + b"|" + bytes(im_array)
        self.send_data(data)

    def recv_image(self, data, sock1addr):
        try:
            bytes_shape, im_data = data.split(b'|', 1)
            shape = eval(bytes_shape)
            mode = shape2mode[len(shape)]

            im_array = bytes2ndarray(im_data, mode, shape2size(shape))
            # im_array = im_array.reshape(shape)

            # g.get("unit_curr_img").set_image(im_array, "remote_img_temp")
            # 无法由子线程调用Qt主线程处理函数
            self.dataUpdated.emit(im_array)

        except Exception as e:
            logger.error(f"接收的远程数据错误：{e}")
