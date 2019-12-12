# encoding: utf-8

from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np

from util.imgio import bytes2ndarray
from ..broker.protocal import ForwardTrans, BROKER_PORT

from util.log import getLogger
logger = getLogger()

class HerosysImageQtTrans(ForwardTrans, QObject):
    """ 提供pyqtSignal的协议 """
    dataUpdated = pyqtSignal(np.ndarray)
    reglistRecv = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.dict_registers = {}  # UDP: "license": (ip, port)
                                  # TCP: "license": sock_proxy
        self.map_connection = {}  # UDP: (ip, port): (ip2, port2)
                                  # TCP: sock_proxy: sock_proxy2

    def send_image(self, im_array):
        """ 发送包结构：b'(640, 480, 3)|im_array' """
        shape = str(im_array.shape)
        data = shape.encode() + b"|" + bytes(im_array)
        self.send_data(data)

    def on_accept_data(self, data):
        # print("Recv Msg【{}】".format(data[:30]))
        try:
            bytes_shape, im_data = data.split(b'|', 1)
            h, w = eval(bytes_shape)[:2]
            im_array = bytes2ndarray(im_data, "L", (w, h))
            # im_array = im_array.reshape(shape)

            # g.get("unit_curr_img").set_image(im_array, "remote_img_temp")
            # 无法由子线程调用Qt主线程处理函数
            self.dataUpdated.emit(im_array)

        except Exception as e:
            logger.error(f"接收的远程数据错误，舍弃该数据帧：{e}")

    def on_register_list(self, dict_msg):
        dict_ = dict_msg["msg"]
        self.reglistRecv.emit(dict_)


class HerosysImageReqQtTrans(HerosysImageQtTrans):
    def on_connect_break(self, dict_msg):
        """ 对端已经断开，此消息由中间件发出 """
        print("远程对象已断开连接")


class HerosysImageRepQtTrans(HerosysImageQtTrans):
    connBreak = pyqtSignal()

    def on_connect_break(self, dict_msg):
        """ 对端已经断开，此消息由中间件发出 """
        print("远程对象已断开连接")
        # 关闭本地连接
        self.sock.close()  # 会触发本地端client的心跳包发送异常，然后退出程序
        # raise AssertionError("远程对象已断开连接")  # 委托回调 ??
        self.connBreak.emit()
