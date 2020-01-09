#!/usr/bin/env python

# from utils.expy import chdir_topdir
def chdir_topdir(dir_dst, override=False):
    import os, sys
    dir_dst_abs = os.path.abspath(dir_dst)
    os.chdir(dir_dst_abs)
    if override:
        sys.path[0] = dir_dst_abs
    else:
        sys.path.insert(0, dir_dst_abs)

chdir_topdir("../..", True)  # src
# import sys; print(sys.path)
from utils import expy
expy.venv_expand("../env/win64")
expy.site_expand("../env/win64/Lib/rsa")

from utils.base import import_plugin
from multiprocessing import freeze_support

# 注意，此处必须使用 __main__，因为multiprocess.Process() 在Windows环境中：
#     在Windows操作系统中由于没有fork，在创建子进程的时候会自动 import 启动它的这个文件，
# 而在 import 的时候又执行了整个文件。因此如果将process()直接写在文件中就会无限递归创建子进程报错。
# 所以必须把创建子进程的部分使用`if __name__ == "__main__" `判断保护起来，import 的时候，就不会递归运行了。

# 官方解释
# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing

# 尝试打包后添加依赖，运行时自动搜索 ??
# from mvlib import *  # 显式打包opencv与mvlib（用于图像的预处理）

if __name__ == "__main__":
    freeze_support()  # pyinstaller "--onefile" mode 并不适用...
    import app.demo.main  # 显示导入模块，用于pyinstaller导入模块

    app_demo = import_plugin("app.demo.main")
    app_demo.run()
