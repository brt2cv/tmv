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
    parser.add_argument("core", action="store", help="which application to launch")
    parser.add_argument("-l", "--loglevel", action="store", type=int, help="set the logging level")
    return parser.parse_args()


if __name__ == '__main__':
    import logging
    from util.base import import_plugin

    args = getopt()
    if not args.loglevel:  # 设置默认Log-Level
        args.loglevel = 20

    logging.basicConfig(level=args.loglevel)  # 更改全局默认的Level，仅用于未指定Level的logger对象

    #####################################################################
    MAP_APP = {
        "triage": "app/triage/core.py",
    }

    path_app_core = MAP_APP[args.core] if args.core in MAP_APP else args.core
    core = import_plugin(path_app_core)
    core.run()
