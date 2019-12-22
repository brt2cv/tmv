from threading import Thread, Event
from .grabbase import IImageGrabber

from utils.log import getLogger
logger = getLogger()

from ..setting import PluginSettings
setting = PluginSettings()
PROTOCAL = setting.get("broker", "protocal")
if PROTOCAL == "tcp":
    from core.rcp.pub.routine import TcpServer, TcpClient
    TplServer = TcpServer
    TplClient = TcpClient
elif PROTOCAL == "udp_buf":
    from core.rcp.pub.routine import UdpServer, UdpClient
    TplServer = UdpServer
    TplClient = UdpClient
elif PROTOCAL == "udp":
    from core.rcp.broker4img.routine import UdpImgServer, UdpImgClient
    TplServer = UdpImgServer
    TplClient = UdpImgClient
else:
    raise Exception(f"未知的Setting设置：【broker】：protocal:【{PROTOCAL}】")

from core.rcp.rcp4img.protocal import RemoteImageQtTrans
from core.rcp.broker4img.protocal import HerosysImageQtTrans, HerosysImageReqQtTrans, HerosysImageRepQtTrans

class LocalGrabber(IImageGrabber):
    def __init__(self):
        super().__init__()
        self.isPause = False
        self.routine = None

    def _setup(self):
        protocal = RemoteImageQtTrans()
        protocal.dataUpdated.connect(self.transfer)
        self.routine.set_protocal(protocal)

    def setup_server(self, port):
        self.routine = TplServer(port)
        self._setup()

    def setup_client(self, ipaddr, port):
        self.routine = TplClient((ipaddr, port))
        self._setup()

    def listen(self):
        # 局域网数据P2P传输，如为UDP无需启动心跳
        self.routine.listen()

    def transfer(self, im_array):
        """ 由于需要isPause控制，凭空多加了一层转发信号 """
        if self.isPause:
            return
        self.dataUpdated.emit(im_array)

    def pause(self, value: bool):
        self.isPause = value

    def stop(self):
        try:
            self.routine.protocal.connect_close()
        except OSError:
            pass
        self.routine.stop()


class BrokerRequestGrabber(IImageGrabber):
    def __init__(self, ipaddr, port):
        super().__init__()
        # self.isPause = False
        self.routine = TplClient((ipaddr, port))

        protocal = HerosysImageReqQtTrans()
        # protocal.dataUpdated.connect(self.transfer)  # 上传服务，无需处理
        self.routine.set_protocal(protocal)

    def listen(self):
        self.routine.listen(runHeart=True)  # 发送心跳包连接状态

        # 发送license账号
        import uuid
        machine_id = uuid.getnode()
        str_mochine_id = str(machine_id)
        self.routine.protocal.register_assist(str_mochine_id)

    def stop(self):
        try:
            self.routine.protocal.connect_close()
        except OSError:
            pass
        self.routine.stop()


class BrokerReplyGrabber(IImageGrabber):
    def __init__(self, ipaddr, port):
        super().__init__()
        self.isPause = False
        self.routine = TplClient((ipaddr, port))

        protocal = HerosysImageRepQtTrans()  # 提供pyqtSignal
        protocal.dataUpdated.connect(self.transfer)
        self.routine.set_protocal(protocal)

        # 提供一个Signal的包装
        self.reglistRecv = protocal.reglistRecv

    def listen(self):
        """ 连接后，查询列表并返回: dict_requests """
        self.routine.listen(runHeart=True)  # 发送心跳包连接状态

        # 查询当前协助列表
        self.routine.protocal.register_list()

    def connect(self, license):
        self.routine.protocal.connect_to_remote(license)

    def transfer(self, im_array):  # 凭空多加了一层传输 ??
        if self.isPause:
            return
        self.dataUpdated.emit(im_array)

    def pause(self, value: bool):
        self.isPause = value

    def stop(self):
        try:
            self.routine.protocal.connect_close()
        except OSError:
            pass
        self.routine.stop()
