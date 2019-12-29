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
            try:
                from .view.mainwnd import MainWnd
            except ImportError:
                # 适配app/xxx/run.py作为顶级目录启动
                logger.warning("当前并非在项目顶层目录运行...")
                from view.mainwnd import MainWnd

            self.mwnd = MainWnd(None)
        else:
            self.mwnd = callback_mwnd()

        self.mwnd.show()
        def auto_open_testing():
            """ 用于打开图像并写入UndoStack记录 """
            from plugins.file import OpenImageFile
            plugin = OpenImageFile()
            plugin.open("app/mvtool/res/example.jpg")
        # auto_open_testing()
        app.exec_()


""" 全局变量声明
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
