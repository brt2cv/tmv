from utils.log import getLogger
logger = getLogger()

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
            from view.mainwnd import MainWnd

            self.mwnd = MainWnd(None)
        else:
            self.mwnd = callback_mwnd()

        self.mwnd.show()
        # 初始化时载入图像
        def auto_open_testing(saveUndoStack=False):
            """ 用于打开图像并写入UndoStack记录 """
            from utils.base import rpath2curr
            path_example = rpath2curr("res/example.jpg")

            if saveUndoStack:
                from plugins.file import OpenImageFile
                OpenImageFile().open(path_example)
            else:
                from core.imgio import instance
                instance().open_file(path_example)

        auto_open_testing(True)
        # 启动rcp服务
        from core.imgio import instance
        instance().rcp_open()
        app.exec_()
        instance().rcp_close()


""" 全局变量声明
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
