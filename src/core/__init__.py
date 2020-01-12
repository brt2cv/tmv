import os.path as osp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

root_dir = osp.abspath(osp.join(osp.dirname(__file__), ".."))

from utils.gmgr import GlobalObjectManager
g = GlobalObjectManager()

#####################################################################

import time
from utils.log import make_logger
from utils.base import get_caller_path
def getLogger(level=None):
    path_caller = get_caller_path()
    rpath = osp.relpath(path_caller)  # 相对路径
    name = osp.splitext(rpath)[0]
    curr_time = time.strftime('%m-%d-%H-%M-%S', time.localtime())
    output_file = "user/" + curr_time + ".log"
    return make_logger(level, name, output_file)

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
