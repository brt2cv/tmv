import zmq
import numpy as np

class HerosysHidTcpDevice:
    def __init__(self, ipaddr="tcp://localhost:31581"):
        context = zmq.Context()
        self.sock = context.socket(zmq.PULL)
        self.sock.connect(ipaddr)
        # self.sock.setsockopt(zmq.SUBSCRIBE, b"")

    def __del__(self):
        self.sock.close()

    def read(self):
        bytes_data = self.sock.recv()
        return bytes_data


if __name__ == "__main__":
    from hiddev import extract_img

    hid_io = HerosysHidTcpDevice()
    while 1:
        bytes_data = hid_io.read()
        print(">>>>>", bytes_data[0:4], bytes_data[-4:], "<<<<<", len(bytes_data))
        img = extract_img(bytes_data)
        # print(type(img))