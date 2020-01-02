import os
import json

from utils.gmgr import g
from utils.log import getLogger
logger = getLogger()

# 该模块目前仅用于静态配置，不提供backend.method()的接口

dict_conf = {
    "image_data_format": "channels_last",
    "epsilon": 1e-07,
    "floatx": "float32",
    "backend": "skimage"
}
path_conf = os.path.join(os.environ.get("HOME"), ".mvlib.json")
# path_conf = '$HOME/.mvlib.json'

if os.path.exists(path_conf):
    with open(path_conf, "r") as fp:
        dict_conf = json.load(fp)
else:
    with open(path_conf, "w") as fp:
        json.dump(dict_conf, fp)


def get_backend():
    return dict_conf["backend"]


dict_backend = {
    "pillow":   ["PIL"],
    "numpy":    ["numpy"],
    "scipy":    ["scipy"],
    "skimage":  ["skimage"],
    "opencv":   ["cv2"]
}

def set_backend(name=None):
    """ name = None 仅用于初始化 """
    notInitial = name is not None
    if notInitial:
        assert name in dict_backend, f"未知的后端类型：【{name}】"
        dict_conf["backend"] = name

        with open(path_conf, "w") as fp:
            json.dump(dict_conf, fp)

    g.register("Backend", dict_conf["backend"], forced=True)
    print(f"Using 【{dict_conf['backend']}】 Backend")

    # 由于include()，需要reload()各个子模块
    from . import _import_submodules
    try:
        _import_submodules(notInitial)
    except ModuleNotFoundError:
        print(f"当前后端使用【{get_backend()}】，但未找到依赖库；请更换后端")

#####################################################################
# 类型提升
type_degrade = {
    "opencv"    : "numpy",
    "skimage"   : "scipy",
    "scipy"     : "numpy"
}

def include(backend_type, _curr_type=None) -> bool:
    """ 用于导入依赖：
        if include("opencv"):
            import cv2
        if include("skimage"):
            import skimage
        if include("scipy"):
            import scipy
        if include("numpy"):
            import numpy as np
        if include("pillow"):
            from PIL import Image
    """
    if _curr_type is None:
        _curr_type = get_backend()
    if backend_type == _curr_type:
        return True
    if _curr_type in type_degrade:
        return include(backend_type, type_degrade[_curr_type])
    else:
        return False

def run_backend(
        func_pillow=None,
        func_numpy=None,
        func_opencv=None,
        func_scipy=None,
        func_skimage=None
    ):
    """ 根据设定的后端，选择合适的func接口 """
    map4run = {
        "pillow"    : func_pillow,
        "numpy"     : func_numpy,
        "opencv"    : func_opencv,
        "skimage"   : func_skimage,
        "scipy"     : func_scipy
    }

    def try_run(backend_type):
        # global Backend
        func_run = map4run[backend_type]
        if func_run is None:
            assert backend_type in type_degrade, f"未定义有效的执行函数"
            Backend = type_degrade[backend_type]
            logger.warning(f"未找到【{backend_type}】执行函数，尝试转换低阶类型【{Backend}】")
            return try_run(Backend)
        else:
            return func_run

    Backend = get_backend()
    return try_run(Backend)
