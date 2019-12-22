# 默认获取rcp4img的客户端

from utils.sock.routine import UdpClient, UdpServer
from .rcp4img.protocal import RemoteImageQtTrans

RCP4IMG_ADDR = "127.0.0.1"
RCP4IMG_PORT = 31578

def make_client(ipaddr=RCP4IMG_ADDR, port=RCP4IMG_PORT):
    client = UdpClient((ipaddr, port))
    protocal = RemoteImageQtTrans()
    client.set_protocal(protocal)
    # client.listen()
    return client, protocal  # client.protocal

def make_server(port=RCP4IMG_PORT):
    server = UdpServer(RCP4IMG_PORT)
    protocal = RemoteImageQtTrans()
    server.set_protocal(protocal)
    server.listen()
    return server
