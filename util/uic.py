
###############################################################################
# Name:         uic
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019-12-13
# Version:      [1.1.1]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import os.path
from importlib import import_module
from .debug import get_caller_path

def loadUi_by_Mixin(uifile, instance):
    without_ext = os.path.splitext(uifile)[0]
    # path = without_ext.replace("ui/", "ui2py.")  # 默认规则：将res/ui目录改为res/ui2py
    str_module = without_ext.replace("/", ".")

    module = import_module(str_module)
    try:
        Ui_Form = getattr(module, "Ui_Form")
    except AttributeError:
        # 没有找到更加高效的方式提取class，暂用dir()实现 ??
        for attr in dir(module):
            if attr.startswith("Ui_"):
                Ui_Form = getattr(module, attr)
                break

    # 通过Mixin的方式多继承Ui_Form
    WidgetClass = instance.__class__
    WidgetClass.__bases__ += (Ui_Form,)

    instance.setupUi(instance)


print(f"Uic Mode is [{os.path.splitext(__file__)[1] == '.py'}] debugging")

if os.path.splitext(__file__)[1] != '.py':  # pyc or something...
    _loadUi = loadUi_by_Mixin
else:
    from PyQt5.uic import loadUi as _loadUi

def loadUi(uifile, instance, rpath=True):
    """ uifile相对当前模块的rpath
        instance固定传入self即可。
    """
    if rpath:
        path_caller = get_caller_path()
        path_dir = os.path.dirname(path_caller)
        uifile = os.path.join(path_dir, uifile)

    _loadUi(uifile, instance)
