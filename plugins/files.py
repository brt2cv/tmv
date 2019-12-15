from PyQt5.QtWidgets import QMessageBox
from util.qt5 import dialog_file_select
from core import g
from core.plugin import Plugin

def export_plugin(cls):  # cls并不建议直接提供默认值'DemoDlg'
    return eval(cls)

class OpenImageFile(Plugin):
    def run(self):
        """ override: 无需打开图像 """
        file_path = dialog_file_select(g.get("mwnd"), "Images (*.png *.bmp *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            QMessageBox.warning(g.get("mwnd"), "错误", "请勿选择多张图片")
            return
        path_pic = file_path[0]

        # try:
        #     from core.io import imread
        #     img = imread(path_pic)
        # except Exception as e:
        #     logger.error(f"载入图像失败：{e}")
        #     QMessageBox.warning(self, self.tr("错误"), self.tr("无法载入图像，路径是否含有中文？"))
        #     return
        g.get("canvas").load_image(path_pic)
