from PyQt5.QtWidgets import QMessageBox
from utils.qt5 import dialog_file_select
from core import g
from core.plugin.filter import Filter

from core.undo import UndoIndexError
class Undo(Filter):
    def run(self):
        try:
            im_mgr = g.get("canvas").get_container()
            im_mgr.undo()
            self.update_canvas()
        except UndoIndexError as e:
            g.call("prompt", str(e), 5)

class Redo(Filter):
    def run(self):
        try:
            im_mgr = g.get("canvas").get_container()
            im_mgr.redo()
            self.update_canvas()
        except UndoIndexError as e:
            g.call("prompt", str(e), 5)

class UndoDebugger(Filter):
    def run(self):
        im_mgr = g.get("canvas").get_container()
        im_mgr.stack._debug()

class CurrImageInfo(Filter):
    def _print_info(self, im):
        print(im)

        list_info = []
        print("#"*60)
        list_info.append(f"Shape: 【{im.shape}】")
        list_info.append(f"Size:  【{im.size}】")
        list_info.append(f"Type:  【{im.dtype}】")
        str_info = "\n".join(list_info)
        print(str_info)
        print("#"*60)
        return str_info

    def run(self):
        print(">> canvas显示图像(curr)")
        im_mgr = g.get("canvas").get_container()
        str_info = self._print_info(im_mgr.curr)
        QMessageBox.information(g.get("mwnd"), "图像信息", str_info)

        print(">> canvas存储图像(snap)")
        self._print_info(im_mgr.snap)

from pprint import pprint
from PyQt5.QtWidgets import QInputDialog
class ImgStackScripts(Filter):
    def run(self):
        im_mgr = g.get("canvas").get_container()
        list_scripts = im_mgr.dumps()
        pprint(list_scripts)

        msgbox = QInputDialog(g.get("mwnd"))
        msgbox.setWindowTitle("导出脚本")
        msgbox.resize(400, 10)
        msgbox.setLabelText("已复制到剪切板")
        msgbox.setOptions(QInputDialog.UsePlainTextEditForTextInput)
                          # | QInputDialog.NoButtons)
        msgbox.setOkButtonText("复制")
        msgbox.setCancelButtonText("关闭")
        msgbox.setTextValue("\n".join(list_scripts))
        msgbox.show()
