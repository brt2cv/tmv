from PyQt5.QtWidgets import QWidget

class MainWnd(QWidget):
    def __init__(self, parent, attach=None):
        from utils.qt5 import loadUi
        from utils.gmgr import g

        super().__init__(attach if attach is not None else parent)
        loadUi("ui/wx_mwnd.ui", self)
        g.register("mwnd", self)

        self.setProperty("class", "bkg")  # for qss
        self.resize(400, 300)
        self.move(0, 0)
