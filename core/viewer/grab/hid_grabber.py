from threading import Thread, Event
from .grabbase import IImageGrabber

from core.hid.hiddev import extract_img, HerosysHidDevice

from util.log import make_logger
logger = make_logger(1)

class HidGrabber(IImageGrabber, Thread):
    def __init__(self):
        super().__init__()
        Thread.__init__(self)

        self.isRunning = Event()
        self.isRunning.set()
        self.isPause = Event()

    listen = Thread.start

    def stop(self):
        """ 线程外调用 """
        logger.debug("准备结束HID线程...")
        self.isRunning.clear()
        self.join()  # 等待回收线程

    def run(self):
        logger.debug("启动HID图像传输线程...")
        self.hid_io = HerosysHidDevice()

        while self.isRunning.is_set():
            try:
                self.read_hid()
            except Exception as e:
                logger.error(e)

        logger.debug("结束HID设备")
        self.hid_io.destroy()

    def read_hid(self):
        bytes_data = self.hid_io.read()  # 阻塞，超时500ms
        if bytes_data:
            # logger.debug(f"Recv HID data >> {bytes_data[0:4]}")
            if self.isPause.is_set():
                return

            im_array = extract_img(bytes_data)
            # logger.debug(f"img.shape -->> {im_array.shape}")
            self.dataUpdated.emit(im_array)

    def pause(self, value: bool):
        if value:
            self.isPause.set()
        else:
            self.isPause.clear()

    def alarm(self):
        self.hid_io.cmd_alarm()
