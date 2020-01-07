import os.path as osp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

from utils.gmgr import g
root_dir = osp.abspath(osp.join(osp.dirname(__file__), ".."))


def alert(msg):
    QMessageBox.warning(g.get("mwnd"), "错误", msg)

def info(msg):
    QMessageBox.information(g.get("mwnd"), "通知", msg)

def progress(title, msg, steps):
    progress = QProgressDialog(msg, None, 0, steps)
    # progress = QProgressDialog(None)
    # progress.setLabelText(msg)
    # progress.setRange(0, steps)

    progress.setCancelButton(None)
    progress.setWindowTitle(title)
    # progress.setAutoClose(False)
    progress.setAutoReset(True)
    progress.setMinimumDuration(500)  # 0.5s内能够完成，则不再显示
    # progress.exec_()
    progress.setWindowModality(Qt.WindowModal)
    progress.open()

    import time
    for i in range(steps):
        progress.setValue(i)
        time.sleep(0.1)
        if progress.wasCanceled():
            break
    else:
        progress.setValue(steps)
