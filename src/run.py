#!/usr/bin/env python

###############################################################################
# Name:         Python3-Template Framework
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2020-01-01
# Version:      [2.0.3]
# RCS-ID:       $$
# Copyright:    (c)
# Licence:
###############################################################################

import os.path
import logging

# 当使用Python-embed-runtime时，需要手动加载cwd至sys.path
# import os.path
# curr_dir = os.path.abspath(".")  # os.path.curdir
# if curr_dir not in sys.path:
#     print(f"expy: 动态加载Lib目录【{curr_dir}】")
#     sys.path.append(curr_dir)

from utils import expy
from utils.base import import_plugin

def getopt():
    import argparse

    parser = argparse.ArgumentParser("Python3-exe Template", description="")
    parser.add_argument("main", action="store", help="选择执行的app(传入main.py路径)")
    parser.add_argument("-r", "--runtime", action="store_true", help="使用系统python环境运行")
    parser.add_argument("-l", "--loglevel", action="store", type=int, help="设置logging等级")
    return parser.parse_args()

def expand_lib_dir(list_expand):
    py_lib_dir = os.path.join(dir_env, "/Lib")
    for path in list_expand:
        if path.startswith("$dir/"):
            path = path.replace("$dir", py_lib_dir)
        expy.site_expand(path)

def runApp(path_main, lib_expand: list):
    if lib_expand:
        expand_lib_dir(lib_expand)
    expy.path_expand(os.path.dirname(path_main))  # 用于在app中以顶层路径的方式载入子模块
    main = import_plugin(path_main)
    main.run()


if __name__ == '__main__':
    # 默认的runtime
    dir_env = "../env/win64"
    expy.venv_expand(dir_env)

    args = getopt()
    if not args.loglevel:  # 设置默认Log-Level
        args.loglevel = 20

    logging.basicConfig(level=args.loglevel)  # 更改全局默认的Level，仅用于未指定Level的logger对象

    # 快捷选项
    MAP_APP = {
        "tmv": {
            "path_main": "app/mvtool/main.py"
        },
        "viewer": {
            "path_main": "app/viewer/main.py"
        },
        "triage": {
            "path_main": "app/triage/main.py",
            # "lib_expand": ["$dir/rsa"]
        },
        "ocrkit": {
            "path_main": "app/OCRKit/main.py"
        }
    }

    lib_expand = []
    if args.main in MAP_APP:
        path_main = MAP_APP[args.main]["path_main"]
        lib_expand = MAP_APP[args.main].get("lib_expand", [])
    else:
        path_main = args.main

    runApp(path_main, lib_expand)
