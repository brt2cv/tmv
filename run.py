#!/usr/bin/env python

###############################################################################
# Name:         Python3-Template Framework
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2019-12-12
# Version:      [2.0.2]
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
    parser.add_argument("main", action="store", help="选择执行的app(传入main.py路径)")
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
        "tmv": {
            "path_main": "app/mvtool/main.py"
        },
        "triage": {
            "path_main": "app/triage/main.py",
            "lib_expand": ["$dir/rsa"]
        },
    }

    def expand_lib_dir(list_expand):
        for path in list_expand:
            if path.startswith("$dir/"):
                path = path.replace("$dir", py_lib_dir)
            site_expand(path)

    if args.main in MAP_APP:
        path_main = MAP_APP[args.main]["path_main"]
        lib_expand = MAP_APP[args.main].get("lib_expand", [])
        expand_lib_dir(lib_expand)
    else:
        path_main = args.main

    main = import_plugin(path_main)
    main.run()