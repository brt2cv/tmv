#!/usr/bin/python3

import zmq
from hiddev import HerosysHidDevice

PORT_HID_SCANNER = 31581

if __name__ == "__main__":
    context = zmq.Context()
    sock = context.socket(zmq.PUB)
    sock.bind(f"tcp://*:{PORT_HID_SCANNER}")
    print(f"开启HID扫描服务端：【tcp://*:{PORT_HID_SCANNER}】")

    hid_io = HerosysHidDevice()
    while True:
        bytes_data = hid_io.read()
        # print("Recv HID data >> ", bytes_data[0:4])
        if bytes_data:
            sock.send(bytes_data)
            from hiddev import extract_img
            img = extract_img(bytes_data)

    sock.close()
    hid_io.destruct()
    print("关闭HID扫描服务端")