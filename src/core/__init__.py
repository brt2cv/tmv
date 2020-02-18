import os, os.path as osp
from utils.base import rpath2curr
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

root_dir = osp.abspath(osp.join(osp.dirname(__file__), ".."))

from utils.gmgr import GlobalObjectManager
g = GlobalObjectManager()

from .config import ConfigManager
conf_mgr = ConfigManager()
# 对于core配置，允许直接将ini设定为等级2，即不能通过user重新配置：
# 原因：类似log的目录，可能在载入user设定之前，配置项已经应用，修改造成前后分裂
conf_mgr.load_conf("core", 2, rpath2curr("config/core.ini"))
conf_mgr.load_conf("app", 0, rpath2curr("config/app.ini"))

#####################################################################

path_logfile = None
def _get_logfile():
    """ 延时加载 """
    global path_logfile
    import time

    dir_log = conf_mgr.get("core", "path", "dir_log")
    if not osp.exists(dir_log):
        os.makedirs(dir_log)

    logfile = conf_mgr.get("core", "path", "logfile")
    if logfile.find("${time}") >= 0:
        curr_time = time.strftime('%m-%d-%H-%M-%S', time.localtime())
        logfile = logfile.replace("${time}", curr_time)
    path_logfile = osp.join(dir_log, logfile)


from utils.log import make_logger
from utils.base import get_caller_path
def getLogger(level=None):
    path_caller = get_caller_path()
    rpath = osp.relpath(path_caller)  # 相对路径
    name = osp.splitext(rpath)[0]
    if path_logfile is None:
        _get_logfile()
    return make_logger(level, name, path_logfile)

def alert(msg):
    QMessageBox.warning(g.get("mwnd"), "错误", msg)

def info(msg):
    QMessageBox.information(g.get("mwnd"), "通知", msg)

def progress(title, msg, steps):
    dlg = QProgressDialog(msg, None, 0, steps)
    # dlg = QProgressDialog(None)
    # dlg.setLabelText(msg)
    # dlg.setRange(0, steps)

    dlg.setCancelButton(None)
    dlg.setWindowTitle(title)
    # dlg.setAutoClose(False)
    dlg.setAutoReset(True)
    dlg.setMinimumDuration(500)  # 0.5s内能够完成，则不再显示
    # dlg.exec_()
    dlg.setWindowModality(Qt.WindowModal)
    dlg.open()

    import time
    for i in range(steps):
        dlg.setValue(i)
        time.sleep(0.1)
        if dlg.wasCanceled():
            break
    else:
        dlg.setValue(steps)


logger = getLogger()
from ctypes import windll
class MainEntrance:
    """ 默认支持License授权的入口类 """
    LicenseID = ""  # "triage"
    LicenseVersion = ""  # v0.6.1
    LicenseCode = ""  # 820871

    def __init__(self):
        self.license_timer = None

    def load_settings(self, path_conf):
        conf_mgr.load_conf("app", 1, path_conf)
        self.LicenseVersion = conf_mgr.get("app", "license", "version")

    def quit_app(self, msg):
        self.mwnd.close()
        windll.user32.MessageBoxW(0, msg, "授权警告", 0)

    def cancel_timer(self):
        """ 取消定时器，否则qt无法正常退出 """
        if self.license_timer and self.license_timer.is_alive():
            self.license_timer.cancel()
            # self.license_timer.join()

    def check_license(self):
        from core.register import LicenseChecker
        checker = LicenseChecker()

        # windll.user32.MessageBoxW(0, "正在检查授权状态...", "授权检查", 0)
        # PostMessage(ptr, WM_CLOSE, IntPtr.Zero, IntPtr.Zero)
        # progress("授权检查", "正在检查授权状态...", 150)

        try:
            state, reason = checker.check([self.LicenseID, self.LicenseVersion])
            if state == 0:
                logger.debug("软件已授权")
                return
            elif state == 1:
                logger.warning(reason)
                return
            else:  # state == 2:
                logger.error(reason)
                windll.user32.MessageBoxW(0, reason, "授权警告", 0)

            from threading import Timer
            trytime = checker.get_trytime()

            # 定时器计时
            self.license_timer = Timer(2 + 60 * trytime,  # 至少等待0.5s，使self.mwnd启动
                                       lambda: self.quit_app(reason))
            self.license_timer.start()

        except (ConnectionError, TimeoutError):
            from threading import Timer
            machine_node = checker.manual_authorize()

            msg = f"无法连接到授权服务器，请手动导入授权证书（授权码：{machine_node}）"
            # msg = str(e)
            windll.user32.MessageBoxW(0, msg, "授权警告", 0)
            self.license_timer = Timer(6, lambda: self.quit_app(
                                       "软件尚未授权，即将关闭"))

            self.license_timer.start()

    def run_pyqt5(self, MainWndClass, check_license: bool):
        from PyQt5.QtWidgets import QApplication

        app = QApplication([])
        if check_license:
            self.check_license()

        self.mwnd = MainWndClass(None)
        self.mwnd.show()
        self.after_mwnd_show()

        app.exec_()
        self.cancel_timer()

    def after_mwnd_show(self):
        """ 在初始化完成后的动作，一般用于自动加载（测试） """

    def run(self):
        """ 需要在子类中定义实际运行的调用过程 """
