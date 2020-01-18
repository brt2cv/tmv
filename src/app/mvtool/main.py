from ctypes import windll
from core import getLogger
logger = getLogger()

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj

class ModulePlugin:
    def __init__(self):
        self.license_timer = None

    def run(self):
        self.load_settings()
        self.run_pyqt5()

    def load_settings(self):
        from core import conf_mgr, rpath2curr
        conf_mgr.load_conf("app", 1, rpath2curr("config/settings.ini"))

    def check_license(self):
        from core.register import LicenseChecker
        from core import progress

        # windll.user32.MessageBoxW(0, "正在检查授权状态...", "授权检查", 0)
        # PostMessage(ptr, WM_CLOSE, IntPtr.Zero, IntPtr.Zero)
        progress("授权检查", "正在检查授权状态...", 150)

        try:
            checker = LicenseChecker()
            state, reason = checker.check('experienced')
            if state == 0:
                logger.debug("软件已授权")
                return
            elif state == 1:
                logger.warning(reason)
                return
            else:  # state == 2:
                logger.error(reason)

            from threading import Timer
            trytime = checker.get_trytime()
            # 定时器计时
            self.license_timer = Timer(2 + 60 * trytime,  # 至少等待0.5s，使self.mwnd启动
                                       lambda: self.quit_app(reason))
            self.license_timer.start()

        except (ConnectionError, TimeoutError) as e:
            # import sys
            # msg = "无法连接到授权服务器，请手动导入授权证书"
            # windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            # sys.exit()
            from threading import Timer

            # msg = "无法连接到授权服务器，非授权状态下提供10min的试用时长"
            msg = str(e)
            windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            self.license_timer = Timer(6, lambda: self.quit_app(
                                       "试用已到期，请尝试连接服务器获取授权证书"))
            self.license_timer.start()

    def quit_app(self, msg):
        self.mwnd.close()
        windll.user32.MessageBoxW(0, msg, "授权警告", 0)

    def cancel_timer(self):
        """ 取消定时器，否则qt无法正常退出 """
        if self.license_timer and self.license_timer.is_alive():
            self.license_timer.cancel()
            # self.license_timer.join()

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        # self.check_license()

        if callback_mwnd is None:
            from .view.mainwnd import MainWnd
            self.mwnd = MainWnd(None)
        else:
            self.mwnd = callback_mwnd()

        self.mwnd.show()

        #####################################################################
        from core.imgio import ImgIOManager
        from utils.base import rpath2curr

        imgio_mgr = ImgIOManager()
        path_example = rpath2curr("res/example.jpg")
        imgio_mgr.open_file(path_example)

        app.exec_()
        imgio_mgr.rcp_stop()
        self.cancel_timer()


""" 全局变量声明
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
