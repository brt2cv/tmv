from utils.log import getLogger
logger = getLogger()

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj

class ModulePlugin:
    def run(self):
        self.load_settings()
        self.run_pyqt5()

    def load_settings(self):
        from utils.gmgr import g
        from utils.settings import IniConfigSettings, rpath2curr

        settings = IniConfigSettings()
        settings.load(rpath2curr("config/settings.ini"))
        g.register("settings", settings)

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        if callback_mwnd is None:
            from view.mainwnd import MainWnd

            self.mwnd = MainWnd(None)
        else:
            self.mwnd = callback_mwnd()

        self.mwnd.show()

        #####################################################################
        from core.imgio import ImgIOManager
        imgio_mgr = ImgIOManager()

        # 自动打开图像并写入UndoStack记录
        path_example = rpath2curr("res/example.jpg")
        imgio_mgr.open_file(path_example)

        # 启动rcp服务
        app.exec_()
        imgio_mgr.rcp_stop()


""" 全局变量声明
g.get("settings"): IniConfigSettings()
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
