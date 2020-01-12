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
