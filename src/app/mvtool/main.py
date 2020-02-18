from ctypes import windll
from core import getLogger
logger = getLogger()

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj


from core import MainEntrance
class ModulePlugin(MainEntrance):
    LicenseID = "mvtool"

    def run(self):
        from utils.base import rpath2curr
        self.load_settings(rpath2curr("config/settings.ini"))

        from .view.mainwnd import MainWnd
        self.run_pyqt5(MainWnd, check_license=False)

    def after_mwnd_show(self):
        from core.imgio import ImgIOManager
        from utils.base import rpath2curr

        imgio_mgr = ImgIOManager()
        path_example = rpath2curr("res/example.jpg")
        imgio_mgr.open_file(path_example)


""" 全局变量声明
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
