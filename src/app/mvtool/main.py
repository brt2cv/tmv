from utils.log import getLogger
logger = getLogger()

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj

class ModulePlugin:
    def __init__(self):
        self.license_timer = None

    def __del__(self):
        print("exit...")
        if self.license_timer and self.license_timer.is_alive():
            self.license_timer.cancel()
            # self.license_timer.join()

    def run(self):
        self.load_settings()
        self.run_pyqt5()

    def load_settings(self):
        from utils.gmgr import g
        from utils.settings import IniConfigSettings, rpath2curr

        settings = IniConfigSettings()
        settings.load(rpath2curr("config/settings.ini"))
        g.register("settings", settings)

    def check_license(self):
        from ctypes import windll
        from core.register import checker
        from core import progress

        # windll.user32.MessageBoxW(0, "正在检查授权状态...", "授权检查", 0)
        # PostMessage(ptr, WM_CLOSE, IntPtr.Zero, IntPtr.Zero)
        progress("授权检查", "正在检查授权状态...", 150)

        try:
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
            def quit_app():
                from ctypes import windll
                self.mwnd.close()
                windll.user32.MessageBoxW(0, reason, "授权警告", 0)

            self.license_timer = Timer(2 + 60 * trytime, quit_app)  # 至少等待0.5s，使self.mwnd启动
            self.license_timer.start()

        except (ConnectionError, TimeoutError):
            # import sys
            # msg = "无法连接到授权服务器，请手动导入授权证书"
            # windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            # sys.exit()
            from threading import Timer
            def quit_app():
                self.mwnd.close()
                windll.user32.MessageBoxW(0, "试用已到期，请尝试连接服务器获取授权证书",
                                          "授权警告", 0)

            msg = "无法连接到授权服务器，非授权状态下提供10min的试用时长"
            windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            self.license_timer = Timer(6, quit_app)
            self.license_timer.start()

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        # self.check_license()

        if callback_mwnd is None:
            from view.mainwnd import MainWnd

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


""" 全局变量声明
g.get("settings"): IniConfigSettings()
g.get("mwnd")
g.get("canvas"): ScrollCanvas()
g.call("prompt"): mwnd.status_bar.showMessage()

"""
