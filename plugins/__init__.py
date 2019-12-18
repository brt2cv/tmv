from .file import *
from .edit import *
from .color import *
from .morphology import *

from core.plugin.adapter import asFilter, IpyPlugin
def export_plugin(cls_name: str):
    cls_obj = eval(cls_name)
    if issubclass(cls_obj, IpyPlugin):
        return asFilter(cls_obj)
    else:
        return cls_obj
