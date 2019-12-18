from util.base import import_plugin as util_plugin
# from plugins import export_plugin

def import_plugin(module, cls_name):
    return util_plugin(module, cls_name=cls_name)

class Plugin:
    def run(self):
        """ Plugin的运行函数 """
