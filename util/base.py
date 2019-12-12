###############################################################################
# Name:         base(基础功能集成)
# Usage:
# Author:       Bright Li
# Modified by:
# Created:      2019-12-11
# Version:      [0.1.0]
# RCS-ID:       $$
# Copyright:    (c) Bright Li
# Licence:
###############################################################################

import os.path
import sys

# from .log import make_logger
# logger = make_logger()

isPy3 = sys.version_info.major >= 3
# isPy36 = sys.version_info[0:2] >= (3, 6)

if isPy3:
    if sys.version_info[0:2] >= (3, 6):
        from pathlib import Path
        def isPath(f):
            return isinstance(f, (bytes, str, Path))
    else:
        def isPath(f):
            return isinstance(f, (bytes, str))

def isDir(f):
    return isPath(f) and os.path.isdir(f)

#####################################################################

def singleton(cls):
    # 对于单例类，无法通过继承的方式节省代码
    _instance = {}  # 略显丑陋
    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

#####################################################################

class Deletable:
    def __init__(self):
        super().__init__()
        self.isDel = False

    def __del__(self):
        # logger.debug("__del__")
        if not self.isDel:
            self.destroy()

    def destroy(self):
        self.isDel = True

#####################################################################
from importlib import import_module  # reload

def path2module(path):
    if os.path.isabs(path):
        print("请使用相对路径载入项目模块")
        return

    without_ext, _ = os.path.splitext(path)
    module = without_ext.replace("/", ".")
    return module


class IPluginObject:
    def run(self, *args, **kwargs):
        pass

def import_plugin(module, package=None, **kwargs):
    """ module:
          - 'top/package/module.py'
          - "top.package.module"
    """
    if isinstance(module, str):
        if module.find("/") >= 0 or module.rfind(".py") >= 0:
            module = path2module(module)
        module = import_module(module, package)

    plugin_obj = module.export_plugin(**kwargs)
    return plugin_obj

# def export_plugin():
#     """ return a Plugin-Class Object """
#     return plugin_obj

#####################################################################
import threading

def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func
