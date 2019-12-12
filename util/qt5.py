
###############################################################################
# Name:         qt5_ext
# Purpose:      a simple packaging of Qt5 API
# Author:       Bright Li
# Modified by:
# Created:      2019-11-28
# Version:      [1.0.1]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

from PyQt5.QtWidgets import QLayout, QWidget

qss_frame_color = """\
QWidget[whatsThis="frame"] {
    background-color: rgb(228, 231, 233);
    border-radius: 10px;
}"""

def extract_widgets(layout1wx, **kwargs):
    """
    output:
        - list: [("obj_name", widget), (xx, yy), ... ]
        - dict: {
                    "btn_id"    : QPushButton-Object,
                    "btn_id_2"  : QPushButton-Object,
                    ...
                }

    params:
        name    [str]: 根据widget的objectName，查找指定对象（递归，返回list）；
                       如未找到返回None；
        index   [int]: 根据该layout对象addWidget的顺序，提取widget对象；
                       如int参数越界，抛出异常
        type    [cls]: 查找第一个指定类型的widget对象，如未找到返回None
        pypes   (cls): 输入多个可选qt控件类型（Tuple），返回全部符合条件的对象
        all          : 返回layout中所有widget对象的映射字典
    """
    if "name" in kwargs:
        obj_name = kwargs["name"]
        qt_type = kwargs.get("type", QWidget)
        return layout1wx.findChild(qt_type, name=obj_name)  # return a list

    if isinstance(layout1wx, QLayout):
        layout = layout1wx
    else:
        layout = layout1wx.layout()
        if not layout:
            raise Exception("This containenr [{}] has NO layout.".format(layout1wx))

    if "index" in kwargs:
        # 如index越界，则程序执行异常
        index = kwargs["index"]
        if index < 0:
            index = layout.count() -1
        return layout.itemAt(index).widget()  # 直接输出(name,wx_obj)

    collection = []  # object: index

    args_type = kwargs.get("type")
    args_types = kwargs.get("types")
    args_all = kwargs.get("all")

    for index in range(layout.count()):
        layout_item = layout.itemAt(index)
        sub_widget = layout_item.widget()  # 获取到widget对象
        if sub_widget is None:
            continue

        elif (args_type and isinstance(sub_widget, args_type)) or \
                 (args_types and sub_widget not in args_types) or \
                 args_all:
            # wx_name = sub_widget.objectName()
            collection.append(sub_widget)

    return collection

#####################################################################

import os.path
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon

def set_label_image(qlabel, path_pic, size=None, scale_type=0):
    """ Qt.IgnoreAspectRatio:   0  # 填充
        Qt.KeepAspectRatio:    1  # 保持比例，按最长边对齐
        Qt.KeepAspectRatioByExpanding: 2  # 保持比例，最短边对齐
    """
    qImg = QPixmap(path_pic)
    if size:
        qImg.scaled(*size, scale_type)

    qlabel.setScaledContents(True)
    qlabel.setPixmap(qImg)

def set_button_image(button, path_pic=None):
    obj_name = "tmp"
    button.setObjectName(obj_name)
    # 使用border-image图像，图像整体缩放（若使用background-image，则使用默认尺寸层叠）
    button.setStyleSheet("#{}{{border-image:url({})}}".format(obj_name, path_pic))

def set_bkg_image(qt_obj, path_pic=None, way="QSS", **kwargs):
    """ 请注意，Qt对jpg的支持不如png，所以请尽量使用png图片格式 """
    if path_pic and not os.path.exists(path_pic):
        raise Exception(f"不存在图像文件路径【{path_pic}】")

    if way == "QSS":
        if "color" in kwargs:
            # 仅用以设置背景色
            qt_obj.setStyleSheet("background-color:{};".format(kwargs["color"]))
            return
        else:
            # 使用样式表，设置背景图片
            obj_name = qt_obj.objectName()
            if not obj_name:
                obj_name = "tmp"
                qt_obj.setObjectName(obj_name)
            # 可换用 background-image, border-image 或 image
            qt_obj.setStyleSheet("#{}{{border-image:url({})}}".format(obj_name, path_pic))

    elif way == "icon":
        """ 针对 QAbstractButton 等图元类型设置背景图 """
        # bitmap = QPixmap(path_pic)
        icon = QIcon(path_pic)  # QIcon(bitmap)

        qt_obj.setIcon(icon)  # 限制：无法拉伸Icon图片，故只能让按钮适应图片
        qt_obj.setIconSize(qt_obj.size())

        # qt_obj.setFixedSize(bitmap.size())
        # qt_obj.setMask(bitmap.mask())

    elif way == "palette":
        # 默认使用画刷
        palette	= QPalette()
        palette.setBrush(QPalette.Background, # Window
                        QBrush(QPixmap(path_pic)))
        if not qt_obj.autoFillBackground():
            qt_obj.setAutoFillBackground(True)  # 设置图片填充
        qt_obj.setPalette(palette)

    else:
        raise Exception("Unknown param 'way' = [{}]".format(way))


from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout

def dialog_file_select(parent, str_filter=None, canMutilSelect=False, onlyDir=False, saveSuffix=None):
    """ return a list of path (支持多选) """
    # caller = self.sender
    dialog = QFileDialog(parent)
    if canMutilSelect:
        dialog.setFileMode(QFileDialog.ExistingFiles)

    if onlyDir:
        dialog.setFileMode(QFileDialog.Directory)  # 只显示目录
        dialog.setOption(QFileDialog.ShowDirsOnly)
    # else:
    #     dialog.setFileMode(QFileDialog.AnyFile)

    if str_filter:
        dialog.setNameFilter(str_filter)  # "Images (*.png *.xpm *.jpg)"

    if saveSuffix:
        dialog.setDefaultSuffix(saveSuffix)

    if dialog.exec():
        list_path = dialog.selectedFiles()
        return list_path

def attach_widget(parent, widget, noInnerMargins=False, noOuterMargins=False):
    outer_layout = parent.layout()
    if outer_layout is None:
        outer_layout = QVBoxLayout(parent)
    if noOuterMargins:
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
    if noInnerMargins:
        inner_layout = widget.layout()
        if inner_layout:
            inner_layout.setContentsMargins(0, 0, 0, 0)
            # inner_layout.setSpacing(0)
    outer_layout.addWidget(widget)

def make_dialog(parent, func_wx_create, title=None, size=None, path_icon=None):
    dialog = QDialog(parent)
    if title:
        dialog.setWindowTitle(title)
    if path_icon:
        dialog.setWindowIcon(QIcon(path_icon))
    if size:
        dialog.resize(*size)
    QVBoxLayout(dialog)

    unit_widget = func_wx_create(parent=parent, attach=dialog)
    attach_widget(dialog, unit_widget, noOuterMargins=True)
    return dialog

class DialogWrapper(QDialog):
    def __init__(self, parent, title=None, size=None, path_icon=None):
        super().__init__(parent)
        self.parent = parent

        if title:
            self.setWindowTitle(title)
        if path_icon:
            self.setWindowIcon(QIcon(path_icon))
        if size:
            self.resize(*size)

        self.setLayout(QVBoxLayout(self))

    def load_plugin(self, str_module, __file__=None, **kwargs):
        from util.debug import import_plugin

        wx_plugin = import_plugin(str_module, parent=self.parent, attach=self, **kwargs)
        # wx_plugin.setObjectName(self.PLUGIN_ID)
        attach_widget(self, wx_plugin, noOuterMargins=True)

    def load_instance(self, WidgetClass, **kwargs):
        wx_instance = WidgetClass(parent=self.parent, attach=self, **kwargs)
        attach_widget(self, wx_instance, noOuterMargins=True)

    def get_widget(self):
        wx_plugin = extract_widgets(self, index=0)
        return wx_plugin

    # 虽然可以使用特定的回调，但需要特殊处理传参。推荐使用猴子补丁，重写closeEvent()
    # def closeEvent(self, event):
    #     self.close_callback()


def window_center(parent, window):
    pos = window.pos()
    x, y = pos.x(), pos.y()
    size = parent.size()
    width, height = size.width(), size.height()
    center = (x + width/2, y + height/2)
    return center

def show_dialog_at_center(parent, subwindow):
    pos = parent.pos()
    x, y = pos.x(), pos.y()
    size = parent.size()
    width, height = size.width(), size.height()
    center = (x + width/2, y + height/2)

    sub_size = subwindow.size()
    width, height = sub_size.width(), sub_size.height()

    pos_related_parent = center[0] - width /2, center[1] - height /2
    subwindow.move(*pos_related_parent)

    subwindow.show()
