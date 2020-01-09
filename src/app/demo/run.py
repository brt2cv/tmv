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

chdir_topdir("../..", False)  # src
# import sys; print(sys.path)
from utils import expy
expy.venv_expand("../env/win64")
expy.site_expand("../env/win64/Lib/rsa")


if __name__ == "__main__":
    from utils.base import import_plugin

    # app_demo = import_plugin("app.demo.main")
    app_demo = import_plugin("main", package=__package__)
    app_demo.run()
