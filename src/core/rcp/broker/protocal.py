# encoding: utf-8

from utils.sock.trans import TransBase, json2dict, dict2json

from utils.log import getLogger
logger = getLogger()

# BROKER_ADDR = "111.67.199.27"
BROKER_ADDR = "127.0.0.1"
BROKER_PORT = 31611

class ForwardTrans(TransBase):
    """ 中间件转发协议 """
    def __init__(self):
        super().__init__()

        self.dict_registers = {}  # UDP: "license": (ip, port)
                                  # TCP: "license": sock_proxy
        self.map_connection = {}  # UDP: (ip, port): (ip2, port2)
                                  # TCP: sock_proxy: sock_proxy2

    def reply(self, msg: bytes, sock1addr=None):
        # logger.debug("接收到消息：【{}】".format(msg))
        msg_type, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            dict_msg = json2dict(msg_body)
            if dict_msg["type"] == "Register Assist":
                self.reply_register_assist(dict_msg, sock1addr)
            elif dict_msg["type"] == "Register List":
                self.reply_register_list(dict_msg, sock1addr)
            elif dict_msg["type"] == "Connect to Remote":
                self.reply_connect_remote(dict_msg, sock1addr)
            elif dict_msg["type"] == "Connection Shutdown":
                self.reply_connect_close(dict_msg, sock1addr)
            else:
                err = "Unkown command [{}]".format(msg)
                self.send_error(err.encode(), sock1addr)

        elif self.check_data(msg):
            # logger.debug("转发数据【{}】".format(msg))
            self.forward_data(msg, sock1addr)

        else:
            err = "Unkown request [{}]".format(msg)
            self.send_error(err.encode(), sock1addr)

    def parse_reply(self, msg: bytes):
        # logger.debug("接收到回复：【{}】".format(msg))
        msg_type, msg_body = self.sock.msg_split(msg)

        if self.check_cmd(msg):
            dict_msg = json2dict(msg_body)
            if dict_msg["type"] == "Register Assist":
                self.on_register_assist(dict_msg)
            elif dict_msg["type"] == "Register List":
                self.on_register_list(dict_msg)
            elif dict_msg["type"] == "Connect to Remote":
                self.on_connect_remote(dict_msg)
            elif dict_msg["type"] == "Connection Break":
                self.on_connect_break(dict_msg)
            elif dict_msg["type"] == "Request Accept":
                self.on_assisted(dict_msg)
            else:
                print("未解析命令【{}】".format(msg))

        elif self.check_data(msg):
            # logger.debug("接收到数据【{}】".format(msg_body))
            self.on_accept_data(msg_body)

        else:
            logger.error("Fail to parse the message【{}】.".format(msg))

    def reply_conn_break(self, socket1addr):
        """ 无法确认当前对象是request or reply """
        if isinstance(socket1addr, tuple):  # UDP
            self._shutdown_udp(socket1addr)
        else:
            self._shutdown_tcp(socket1addr)

    def _shutdown_udp(self, addr):
        for key, value in self.dict_registers.items():  # UDP: "license": (ip, port)
            if value == addr:
                del self.dict_registers[key]
                break

        if addr in self.map_connection:  # UDP: (ip, port): (ip2, port2)
            conn = self.map_connection[addr]
            self.send_cmd(dict2json({"type": "Connection Break"}), conn)
            del self.map_connection[addr]
            del self.map_connection[conn]

    def _shutdown_tcp(self, raw_sock):
        for key, value in self.dict_registers.items():  # TCP: "license": sock_proxy
            value_raw_sock = value.socket
            if value_raw_sock == raw_sock:
                del self.dict_registers[key]
                break

        for key, value in self.map_connection.items():  # TCP: sock_proxy: sock_proxy2
            key_raw_sock = key.socket
            if key_raw_sock == raw_sock:
                self.send_cmd(dict2json({"type": "Connection Break"}), value)
                # key.close()  # 警告，不要在Protocal中关闭sock，其生命周期由Routine管理
                # value.close()
                del self.map_connection[key]
                del self.map_connection[value]  # 会强制关闭另一端的socket
                break

    #####################################################################

    def connect_close(self):
        """ 主动断开，发送通知消息 """
        self.send_cmd(dict2json({"type": "Connection Shutdown"}))

    def reply_connect_close(self, dict_msg, sock1addr):
        """ 如果重写，请继承父类 super().reply_connect_close(sock1addr) """
        self.reply_conn_break(sock1addr)

    def on_connect_break(self, dict_msg):
        """ 对端已经断开，此消息由中间件发出 """
        logger.debug("远程对象已断开连接")
        # 关闭本地连接
        self.sock.close()  # 会触发本地端client的心跳包发送异常，然后退出程序
        # raise AssertionError("远程对象已断开连接")  # 委托回调 ??

    def register_assist(self, license):
        bytes_data = dict2json({
            "type": "Register Assist",
            "msg": license
        })
        self.send_cmd(bytes_data)

    def reply_register_assist(self, dict_msg, sock1addr):
        license_num = dict_msg["msg"]
        if license_num in self.dict_registers:
            already = self.dict_registers[license_num]
            dict_msg["msg"] = "当前序列号已申请远程协助【{}】".format(already)
            self.send_cmd(dict2json(dict_msg), sock1addr)
            return

        # if isinstance(sock1addr, tuple):  # UDP协议
        # else:  # TCP协议
        #     addr = sock1addr.socket.getpeername()
        self.dict_registers[license_num] = sock1addr

        dict_msg["msg"] = "true"
        self.send_cmd(dict2json(dict_msg), sock1addr)

    def on_register_assist(self, dict_msg):
        print("注册回复：", dict_msg["msg"])

    def register_list(self):
        bytes_data = dict2json({"type": "Register List"})
        self.send_cmd(bytes_data)

    def reply_register_list(self, dict_msg, sock1addr):
        dict_ = {}  # license: "222.182.100.1:31610"
        for key, value in self.dict_registers.items():
            if not isinstance(value, tuple):
                # value is TcpProxy
                value = value.socket.getpeername()
            dict_[key] = "{}:{}".format(*value)

        dict_msg["msg"] = dict_
        self.send_cmd(dict2json(dict_msg), sock1addr)

    def on_register_list(self, dict_msg):
        print("协助申请列表：", dict_msg["msg"])

    def connect_to_remote(self, ip_addr):
        bytes_data = dict2json({"type": "Connect to Remote", "msg": ip_addr})
        self.send_cmd(bytes_data)

    def reply_connect_remote(self, dict_msg, sock1addr):
        if sock1addr in self.map_connection:
            dict_msg["msg"] = "你正在协助远程客户端【{}】".format(sock1addr)
            self.send_cmd(dict2json(dict_msg), sock1addr)
            return

        # 回复待连接的IPADDR
        # host, port = dict_msg["msg"].split(":")
        # port = int(port)
        # conn_to = (host, port)

        # if conn_to not in list(self.dict_registers.values()):
        #     dict_msg["msg"] = "未知的协助对象【{}】".format(conn_to)
        #     self.send_cmd(dict2json(dict_msg), sock1addr)
        #     return

        # 回复待连接的LICENSE
        license = dict_msg["msg"]

        if license not in list(self.dict_registers.keys()):
            dict_msg["msg"] = "未知的协助对象【{}】".format(license)
            self.send_cmd(dict2json(dict_msg), sock1addr)
            return
        else:
            conn_to = self.dict_registers[license]

        if conn_to in self.map_connection:
            dict_msg["msg"] = "协助对象已连接到其他客户端【{}】".format(conn_to)
            self.send_cmd(dict2json(dict_msg), sock1addr)
            return

        self.map_connection[sock1addr] = conn_to
        # 对调，但对于映射重写，不能删除原对调pair
        self.map_connection[conn_to] = sock1addr
        logger.debug(self.map_connection)

        dict_msg["msg"] = "true"
        self.send_cmd(dict2json(dict_msg), sock1addr)
        self.send_cmd(dict2json({"type": "Request Accept"}), conn_to)

    def on_connect_remote(self, dict_msg):
        if dict_msg["msg"] == "true":
            self.on_connected(dict_msg)
        else:
            print("协助连接失败：【{}】".format(dict_msg['msg']))

    def forward_data(self, msg, sock1addr):
        if sock1addr not in self.map_connection:
            err = "未能连接到对端计算机（连接已中断）"
            self.send_error(err.encode(), sock1addr)
            return

        target = self.map_connection[sock1addr]
        _, msg_body = self.sock.msg_split(msg)
        logger.debug("转发数据【{}...】to【{}】".format(msg_body[:30], target))
        self.send_data(msg_body, target)

    def on_connected(self, dict_msg):
        # 连接到远程计算机
        print("协助连接成功")

    def on_assisted(self, dict_msg):
        # 协助连接成功后，发送测试数据
        print("已获取到远程协助")

    def on_accept_data(self, data):
        # 接收到数据
        print("Recv Msg【{}】...".format(data[:30]))


class RequestForwardTrans(ForwardTrans):
    def on_connect_break(self, dict_msg):
        """ 对端已经断开，此消息由中间件发出 """
        print("远程对象已断开连接")


class ReplyForwardTrans(ForwardTrans):
    def on_connect_break(self, dict_msg):
        """ 对端已经断开，此消息由中间件发出 """
        print("远程对象已断开连接")
        # 关闭本地连接
        self.sock.close()  # 会触发本地端client的心跳包发送异常，然后退出程序
        # raise AssertionError("远程对象已断开连接")  # 委托回调 ??
