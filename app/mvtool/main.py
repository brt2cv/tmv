from util.log import getLogger
logger = getLogger(1)

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj

class ModulePlugin:
    def run(self):
        self.run_pyqt5()

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        if callback_mwnd is None:
            try:
                from .view.mainwnd import MainWnd
            except:
                from view.mainwnd import MainWnd
                print("________________________")
            self.mwnd = MainWnd(None)
        else:
            self.mwnd = callback_mwnd()

        self.mwnd.show()
        self.mwnd.canvas.load_image("tmp/test.jpg")
        app.exec_()


def documents():  # never called...
    """ 全局变量声明 """
    g.get("mwnd")
    g.get("canvas")
