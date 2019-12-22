# 加载特定的venv环境
from utils.expy import path_append
path_append('runtime/win32/python37/lib')

# # 加载全局设置
# from .setting import PluginSettings
# setting = PluginSettings()


def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj


class ModulePlugin:
    def run(self):
        self._register_global_variable()
        self.run_pyqt5()

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        if callback_mwnd is None:
            from .view.mainwnd import MainWnd
            mwnd = MainWnd()
        else:
            mwnd = callback_mwnd()

        mwnd.show()
        app.exec_()

    def _register_global_variable(self):
        pass