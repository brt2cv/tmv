from threading import Thread, Event
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
from ..hiddev import HerosysHidDevice, extract_img
from .hidsub import HerosysHidTcpDevice

from utils.log import getLogger
logger = getLogger(10)

class HerosysHidThread(Thread, QObject):
    dataUpdated = pyqtSignal(np.ndarray)

    def __init__(self, ipaddr=None):
        Thread.__init__(self)
        QObject.__init__(self)
        self.setDaemon(True)

        self.isRunning = Event()
        self.isRunning.set()

        self.hid_io = HerosysHidTcpDevice(ipaddr) if ipaddr else HerosysHidDevice()  # 使用远程读码器

    def run(self):
        logger.debug("启动HID图像传输线程...")
        while self.isRunning.is_set():
            bytes_data = self.hid_io.read()
            if bytes_data:
                logger.debug(f"Recv HID data >> {bytes_data[0:4]}")
                im_array = extract_img(bytes_data)
                self.dataUpdated.emit(im_array)
        logger.debug("结束HID线程")

    def stop(self):
        logger.debug("准备结束HID线程...")
        self.isRunning.clear()
        # 由于 hid_io.read() 为阻塞操作，所以stop未必保证循环终止??
        # self.hid_io.hid.close()  # 无效


if __name__ == "__main__":
    tid = HerosysHidThread()
    # tid.setDaemon(True)
    tid.start()

    print("..............")
    from time import sleep
    sleep(1)

    tid.stop()
    tid.join()  # 失败……无法从read()阻塞中结束
    print("Thread join done!")
