#!/usr/bin/env python

###############################################################################
# Name:         Python3-Template Framework
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2019-11-14
# Version:      [1.0.1]
# RCS-ID:       $$
# Copyright:    (c)
# Licence:
###############################################################################

import sys
import os.path

# 当使用Python-embed-runtime时，需要手动加载cwd至sys.path
curr_dir = os.path.abspath(".")  # os.path.curdir
if curr_dir not in sys.path:
    print(f"expy: 动态加载Lib目录【{curr_dir}】")
    sys.path.append(curr_dir)

#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("Python3-exe Template", description="")
    parser.add_argument("core", action="store", help="选择执行的app(传入core.py路径)")
    parser.add_argument("-r", "--runtime", action="store_true", help="使用系统python环境运行")
    parser.add_argument("-l", "--loglevel", action="store", type=int, help="设置logging等级")
    return parser.parse_args()


if __name__ == '__main__':
    import logging
    from util.expy import site_expand
    from util.base import import_plugin

    args = getopt()
    if not args.loglevel:  # 设置默认Log-Level
        args.loglevel = 20

    logging.basicConfig(level=args.loglevel)  # 更改全局默认的Level，仅用于未指定Level的logger对象

    #####################################################################
    py_lib_dir = "runtime/win64/Lib"
    py_lib_default = py_lib_dir + "/site-packages"
    site_expand(py_lib_default)

    MAP_APP = {
        "triage": {
            "path_core": "app/triage/core.py",
            "lib_expand": ["$dir/rsa"]
        },
    }

    def expand_lib_dir(lib_expand):
        for path in lib_expand:
            if path.startswith("$dir/"):
                path = path.replace("$dir", py_lib_dir)
            site_expand(path)

    if args.core in MAP_APP:
        path_core = MAP_APP[args.core]["path_core"]
        lib_expand = MAP_APP[args.core]["lib_expand"]
        expand_lib_dir(lib_expand)
    else:
        path_core = args.core

    core = import_plugin(path_core)
    core.run()
