###############################################################################
# Name:         protocal
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2020-01-04
# Version:      [0.0.4]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

from utils.sock.trans import TransBase, json2dict

from utils.imgio import bytes2ndarray, shape2mode
from utils.log import getLogger
logger = getLogger()


class RemoteImageTrans(TransBase):
    """ 文件传输协议
        向服务端发送文件：
    """
    def __init__(self):
        from queue import Queue

        super().__init__()
        self.buffer_img = Queue()

    def reply(self, msg: bytes, sock1addr=None):
        # logger.debug("接收到消息：【{}】".format(msg))
        msg_head, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            logger.error("不支持处理当前命令数据【{}】".format(msg))

        elif self.check_data(msg):
            # logger.debug("转发数据【{}】".format(msg))
            self._recv_image(msg_body, sock1addr)

        else:
            err = "Unkown request [{}]".format(msg)
            self.send_error(err.encode(), sock1addr)

    def parse_reply(self, msg: bytes):
        # logger.debug("接收到回复：【{}】".format(msg))
        msg_head, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            # dict_msg = json2dict(msg_body)
            # if dict_msg["type"] == "Push File":
            #     self.on_push_file(dict_msg)
            # elif dict_msg["type"] == "Pull File":
            #     self.on_pull_file(dict_msg)
            # else:
            print("未解析命令【{}】".format(msg))

        elif self.check_data(msg):
            # logger.debug("接收到数据【{}】".format(msg_body))
            self._recv_image(msg_body, self.sock)

        else:
            logger.error("Fail to parse the message【{}】.".format(msg))

    def send_image(self, im_arr, sock1addr=None):
        """ 发送包结构：b'(640, 480, 3)|im_arr' """
        shape = str(im_arr.shape)
        data = shape.encode() + b"|" + bytes(im_arr)
        self.send_data(data, sock1addr)

    def _recv_image(self, data, sock1addr):
        """ callback(im_arr) """
        try:
            bytes_shape, im_data = data.split(b'|', 1)
            shape = eval(bytes_shape)
            mode = shape2mode(shape)

            im_arr = bytes2ndarray(im_data, mode, shape=shape)
            # 将图像暂存缓冲区
            self.buffer_img.put(im_arr)

        except Exception as e:
            logger.error(f"接收的远程数据错误：{e}")

    def ask_for_image(self, index=-1):
        """ 要求服务器回传图像 """
        if index != -1:
            logger.error("【index】参数尚未启用，敬请期待")
        dict_msg = {
            "type": "Ask for image",
            "index": index  # or name
        }
        self.send_cmd(dict_msg)

    def wait_for_response(self, timeout=None):
        """ 等待回复 """
        return self.buffer_img.get(block=True, timeout=timeout)

    def extract_buffer(self):
        if not self.buffer_img.empty():
            return self.buffer_img.get()


try:
    from PyQt5.QtCore import QObject, pyqtSignal
    import numpy as np
    from utils.gmgr import g
except ImportError:
    pass
else:
    class RemoteImageQtTrans(RemoteImageTrans, QObject):
        dataUpdated = pyqtSignal(np.ndarray)

        def __init__(self):
            super(TransBase, self).__init__()
            QObject.__init__(self)

        def reply(self, msg: bytes, sock1addr=None):
            # logger.debug("接收到消息：【{}】".format(msg))
            msg_head, msg_body = self.sock.msg_split(msg)

            if self.check_cmd(msg):
                logger.debug("命令数据【{}】".format(msg))
                dict_msg = json2dict(msg_body)
                if dict_msg["type"] == "Ask for image":
                    # 从MVTool中载入图像
                    # index = dict_msg["index"]
                    im_arr = g.get("canvas").get_image().get_image()
                    self.send_image(im_arr, sock1addr)

            elif self.check_data(msg):
                # logger.debug("转发数据【{}】".format(msg))
                self._recv_image(msg_body, sock1addr)

            else:
                err = "Unkown request [{}]".format(msg)
                self.send_error(err.encode(), sock1addr)

        def _recv_image(self, data, sock1addr):
            try:
                bytes_shape, im_data = data.split(b'|', 1)
                shape = eval(bytes_shape)
                mode = shape2mode(shape)

                im_arr = bytes2ndarray(im_data, mode, shape=shape)
                # g.get("unit_curr_img").set_image(im_arr, "remote_img_temp")
                # 无法由子线程调用Qt主线程处理函数
                self.dataUpdated.emit(im_arr)

            except Exception as e:
                logger.error(f"接收的远程数据错误：{e}")
