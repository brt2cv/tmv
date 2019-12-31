#!/bin/env python

from .backend import get_backend, set_backend

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

# 模块
# try:
#     from .io import *
#     from .transform import *
#     from .color import *
#     from .pixel import *
#     from .feature import *
#     from .filters import *
#     from .exposure import *
#     from .morphology import *

# except ModuleNotFoundError:
#     print(f"当前后端使用{get_backend()}，但未找到依赖的库文件；请尝试更换后端")


def reload_mvlib():
    from importlib import reload, import_module

    def reload_module(submodule: str):
        module = import_module(submodule, __package__)
        reload(module)

    for str_module in __all__:
        reload_module("." + str_module)

    # reload_module(".io")
    # reload_module(".transform")
    # reload_module(".color")
    # reload_module(".pixel")
    # reload_module(".feature")
    # reload_module(".filters")
    # reload_module(".exposure")
    # reload_module(".morphology")
