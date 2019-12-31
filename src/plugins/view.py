from core import g
from core.plugin import Plugin
from core.plugin.filter import Filter, DialogFilter


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


class HistogramTool(DialogFilter):
    title = "直方图工具"
    buttons = ["Close"]
    view = [{
        "type": "pyplot",
        "name": "Histogram"
    }]

    def run(self):
        def plot(figure):
            # import mvlib
            # hist, bins = mvlib.exposure.histogram()
            axes = figure.add_subplot(111)
            axes.hist(self.get_image().ravel(), 256)

        self.view[0]["plot"] = plot
        super().run()


class FlowChartTool(Plugin):
    def run(self):
        import subprocess
        subprocess.Popen("pyhon3")

