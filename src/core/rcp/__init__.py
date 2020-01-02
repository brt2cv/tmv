# 默认获取rcp4img的客户端

from utils.sock.routine import UdpClient, UdpServer, TcpClient, TcpServer
from .rcp4img.protocal import RemoteImageQtTrans

RCP_ADDR = "127.0.0.1"
RCP_PORT = 31578

def make_client(ipaddr=RCP_ADDR, port=RCP_PORT, byTcp=False):
    ClassClient = TcpClient if byTcp else UdpClient
    client = ClassClient((ipaddr, port))
    protocal = RemoteImageQtTrans()
    client.set_protocal(protocal)
    # client.listen()
    return client  # client.protocal

def make_server(port=RCP_PORT, byTcp=False):
    ClassClient = TcpServer if byTcp else UdpServer
    server = ClassClient(port)
    protocal = RemoteImageQtTrans()
    server.set_protocal(protocal)
    server.listen()
    return server
