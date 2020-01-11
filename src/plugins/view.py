from core import g
from core.plugin import Plugin
from core.plugin.filter import Filter


class NewViewerLabel(Filter):
    def run(self):
        label = g.get("canvas").add_tab_stack()
        g.call("prompt", f"新建标签【{label}】", 5)


class CloseViewerLabel(Filter):
    def run(self):
        tab_canvas = g.get("canvas")
        curr = tab_canvas.currentIndex()
        label = tab_canvas.removeTab(curr)
        g.call("prompt", f"删除标签【{label}】", 5)


# class FlowChartTool(Plugin):
#     def run(self):
#         import subprocess
#         subprocess.Popen("pyhon3")

