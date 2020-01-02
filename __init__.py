#!/bin/env python

import importlib
from .backend import get_backend, set_backend

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]


def _import_submodules(isReload=False):
    def dynamic_import(submodule: str):
        module = importlib.import_module(submodule, __package__)
        if isReload:
            importlib.reload(module)

    for str_module in __all__:
        dynamic_import("." + str_module)

def reload():
    _import_submodules(True)


set_backend(None)  # 初始化backend
