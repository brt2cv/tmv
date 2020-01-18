from core import getLogger
logger = getLogger(1)

def export_plugin():
    """ return a Plugin-Class Object """
    core_obj = ModulePlugin()
    return core_obj

class ModulePlugin:
    def run(self):
        self.timer = None
        self.run_pyqt5()
        # self.run_console()

    def check_license(self):
        from core.register import LicenseChecker
        self.timer = None

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
            def quit_app():
                from ctypes import windll
                # self.mwnd.close()
                windll.user32.MessageBoxW(0, reason, "授权警告", 0)

            self.timer = Timer(2 + 60 * trytime, quit_app)  # 至少等待0.5s，使self.mwnd启动
            self.timer.start()

        except ConnectionError:
            from ctypes import windll
            # import sys
            # msg = "无法连接到授权服务器，请手动导入授权证书"
            # windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            # sys.exit()

            from threading import Timer
            def quit_app():
                # self.mwnd.close()
                windll.user32.MessageBoxW(0, "试用已到期，请尝试连接服务器获取授权证书",
                                          "授权警告", 0)

            msg = "无法连接到授权服务器，非授权状态下提供10min的试用时长"
            windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            self.timer = Timer(6, quit_app)
            self.timer.start()

    def run_pyqt5(self, callback_mwnd=None):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        # self.check_license()

        if callback_mwnd is None:
            from .view.mainwnd import MainWnd
            mwnd = MainWnd(None)
        else:
            mwnd = callback_mwnd()

        mwnd.show()
        self.mwnd = mwnd
        # mwnd.canvas.load_image("tmp/021.jpg")
        app.exec_()

        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            # self.timer.join()

    def run_console(self):
        # from utils.imgio import imread
        from PIL import Image

        path_file = "./test.jpg"
        im = Image.open(path_file)
        print(f"当前图像【{path_file}】的shape = {im.shape}")
