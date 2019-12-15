import os.path as osp
from PyQt5.QtWidgets import QMessageBox

from util.gmgr import g

root_dir = osp.abspath(osp.join(osp.dirname(__file__), ".."))

def alert(msg):
    QMessageBox.warning(g.get("mwnd"), "错误", msg)

