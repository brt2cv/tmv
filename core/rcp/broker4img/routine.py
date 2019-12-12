import struct
from threading import Thread

from ..pub.routine import UdpClient, UdpServer, TIMEOUT_RECV
from util.socket import UdpFrame

from util.log import getLogger
logger = getLogger()

class ImgFrame(UdpFrame):
    """ 取消缓冲区list，改由当下一组数据完成时，即自动将前一组尚未完成的数据，
        空数据区域自动补零（除最后一组外——因为最后一组数据位数未知。
    """
    def __init__(self, socket_=None):
        super().__init__(socket_, buf_num=5)

    def recv(self):
        """ return (data, addr) or None, for unfinished message """
        data_recv, addr = self.socket.recvfrom(self.BUFFER_SIZE)  # 可能丢包、重包、乱序
        # logger.debug("接收【{}】bytes".format(len(data_recv)))

        if not data_recv:
            raise ConnectionError
        if len(data_recv) < self.HEADER_SIZE:
            # raise Exception("非法的数据【{}】".format(data_recv))
            logger.debug("数据长度不足HEADER_SIZE，舍弃数据帧....")
            return
        msg_type, pack_id, pack_idx, nPack = struct.unpack("!IIHH", data_recv[:self.HEADER_SIZE])

        # 对nPack=1的直接处理（不再入栈self.buffer）
        if nPack == 1:
            return data_recv, addr

        if pack_id not in self.buf_seq:
            # 添加新的节点
            buf_item = {}
            buf_item["addr"] = addr
            buf_item["type"] = msg_type
            buf_item["nPack"] = nPack
            self.buffer[pack_id] = buf_item
            self.buf_seq.append(pack_id)

            # logger.info("缓冲栈占用：【{}/{}】".format(len(self.buf_seq), self.buf_num))

        self.buffer[pack_id][pack_idx] = data_recv[self.HEADER_SIZE:]

        if len(self.buf_seq) > self.buf_num:
            # 新增节点后，达到buf_num+1个节点
            logger.debug("强制队首出队")
            pack_repaired = self._rebuild()
            if pack_repaired:
                return pack_repaired
            # 否则继续运行

        elif self._check_whole(self.buf_seq[0]):
            logger.debug("数据包完整接收")
            return self._rebuild()

        # 如果第二包数据即将满帧，则强制清理第一帧
        # elif self._check_whole(self.buf_seq[1]):
        #     pack_repaired = self._rebuild()
        #     if pack_repaired is None:
        #         pack_repaired = self._rebuild()
        #     return pack_repaired

    def _check_whole(self, pack_id):
        return len(self.buffer[pack_id]) == self.buffer[pack_id]["nPack"] + 3

    def _debug_buffer(self):
        """ 打印当前缓冲区（队列）的数据 """
        print("#####################################################################")
        for index, pack_id in enumerate(self.buf_seq):
            buffer = self.buffer[pack_id]
            nPack = buffer["nPack"]
            print("index: ", index)
            print("ID   : ", pack_id)
            print("nPack: ", nPack)
            print("packs: ", list(buffer.keys()))
            print("ratio: ", (len(buffer) - 3) / nPack)

    def _rebuild(self, thresh_raio=0.5):
        """ 当数据不完整时，会尝试修复数据包：空位补零 """
        # self._debug_buffer()  # 打印当前缓冲区（队列）的数据

        pack_id = self.buf_seq.pop(0)
        buffer = self.buffer[pack_id]
        del self.buffer[pack_id]

        addr = buffer["addr"]
        msg_type = buffer["type"]
        nPack = buffer["nPack"]

        #####################################################################
        # 尾包长度计算仅适用于Data数据
        if 0 not in buffer:
            logger.warning("首包丢失，无法组包")
            return

        # 尾帧丢失，无法确定数据长度
        # if (nPack -1) not in buffer:
        #     logger.debug("尾帧丢失，无法修复")
        #     return

        # 实际上可以通过包结构计算尾包长度
        if (nPack - 1) not in buffer:
            # (266, 426)|xxxxx...

            idx_seper = buffer[0].find(b"|")
            if idx_seper < 0:
                logger.warning("未找到分隔符|，该数据非有效的ImgPack，无法组包")
                return

            try:
                h, w = eval(buffer[0][:idx_seper])
                last_size = (h * w + idx_seper + 1) % self.CAPACITY
                buffer[nPack - 1] = bytes(last_size)

            except Exception as e:
                logger.critical(e)
                return

        #####################################################################

        # 计算丢包率
        ratio = (len(buffer) - 3) / nPack
        if ratio < thresh_raio:
            logger.warning("当前包的丢包率【{}】过高，舍弃ImgPack".format(ratio))
            return  # 直接舍弃不足50%数据的包

        data = msg_type.to_bytes(4, byteorder='big') + bytes(8)
        for pack_idx in range(nPack):
            try:
                data += buffer[pack_idx]
            except KeyError:
                data += bytes(self.CAPACITY)

        return data, addr


class UdpImgClient(UdpClient):
    def __init__(self, ipaddr):
        Thread.__init__(self)

        self.sock = ImgFrame()
        self.sock.connect(ipaddr)
        self.sock.settimeout(TIMEOUT_RECV)

        self.isRunning = False
        self.runHeart = False  # UDP默认不启动heart-beat
        self.tid_heart = None
        self.func_clean = None


class UdpImgServer(UdpServer):
    def __init__(self, port):
        Thread.__init__(self)

        self.sock = ImgFrame()
        self.sock.bind(("", port))
        self.sock.settimeout(TIMEOUT_RECV)

        self.isRunning = False
        self.runHeart = False  # UDP默认不启动heart-beat
        self.tid_heart = None
