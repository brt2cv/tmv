#!/bin/env python

from .backend import get_backend, set_backend

# 模块
try:
    from .io import *
    from .transform import *
    from .color import *
    from .filters import *
    from .morphology import *

except ModuleNotFoundError:
    print(f"当前后端使用{get_backend()}，但未找到依赖的库文件；请尝试更换后端")
