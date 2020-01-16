from core.plugin.filter import Filter
from core import g, info


from core.plugin import Plugin
from utils.base import rpath2curr
class ListBoxDialog(Plugin):
    # def __init__(self):

    def run(self):
        from core.menu import ListBoxCreator
        from utils.qt5 import make_dialog

        def make_listbox(parent):
            opt_mgr = ListBoxCreator(parent)
            opt_mgr.load_conf("app/mvtool/config/menu.json")
            return opt_mgr.listbox

        dlg = make_dialog(g.get("mwnd"),
                          make_listbox)
        dlg.show()

# from .color import HistogramTool
class TestPlugin(ListBoxDialog):
    """ 测试插件 """

#####################################################################

import mvlib
from core.plugin.filter import DialogFilter
class SetMvlibBackend(DialogFilter):
    title = "切换MVLIB后端"
    buttons = ["OK"]
    view = [{
        "type": "radio",
        "name": "MVLib Backend",
        "val_range": [["pillow", "numpy", "opencv", "scipy", "skimage"]],
        "para": "backend"
    }]

    def accepted(self):
        str_backend = self.widgets["backend"].get_text()
        mvlib.set_backend(str_backend)
        mvlib.reload()
        g.call("prompt", f"Using【{str_backend}】Backend")

    def _set_radio(self, value):
        return self.view[0]["val_range"][0].index(value)

    def run(self):
        if self.needSetupUi:
            self.setup_ui()
            self.needSetupUi = False
        curr_backend = mvlib.get_backend()
        self.widgets["backend"].set_value(self._set_radio(curr_backend))
        self.show()


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
        info(str_info)

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


