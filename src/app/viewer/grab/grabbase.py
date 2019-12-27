from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np

class IImageGrabber(QObject):
    """ 内含一个线程，用于监听数据；
        数据通过pyqtSignal发送或广播；
    """
    dataUpdated = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

    def listen(self):
        """ 开启监听 """
        pass

    def stop(self):
        """ 结束监听（线程外调用） """
        pass

    def recv_image(self):
        """ self.dataUpdated.emit(im_array) """
        pass

    def pause(self, value: bool):
        pass
