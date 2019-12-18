from PyQt5.QtWidgets import QMessageBox
from util.qt5 import dialog_file_select
from core import g
from core.plugin.filter import Filter

class Undo(Filter):
    def run(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.undo()
        self.update_canvas()

class Redo(Filter):
    def run(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.redo()
        self.update_canvas()

class UndoDebugger(Filter):
    def run(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.stack._debug()
