from core.plugin import Plugin
from core.plugin.filter import Filter, DialogFilterBase, DialogFilter

class AboutMe(Plugin):
    def run(self):
        msgbox = QMessageBox(QMessageBox.NoIcon,
                             "关于",
                             "\n感谢ImagePy的开源，回馈开源社区",
                             parent = g.get("mwnd"))
        msgbox.setDetailedText('版权：Bright Li\nTel: 18131218231\nE-mail: brt2@qq.com')
        msgbox.setIconPixmap(QPixmap("app/mvtool/res/logo.png"))
        msgbox.exec_()

class DemoDlg(DialogFilter):
    format = {
        "mode": "rgb",
        "dtype": "uint8"
    }

    def processing(self, im_arr):
        """ 处理图像的流程 """
        from mvlib.color import rgb2gray
        gray = rgb2gray(im_arr)
        return gray

    def run(self):
        """ 可以控制窗口的尺寸位置 """
        print("This is a plugin with dilog.")
        self.resize(300, 200)
        self.move(0, 20)
        super().run()


import numpy as np
class MatplotDemo(DialogFilterBase):
    """ 使用Matplotlib绘制图表 """
    title = "MatplotDemo"
    view = [{
        "type": "pyplot",
        "name": "MatplotDemo"
    }]

    def run(self):
        def plot(figure):
            """ 回调函数，UnitPlot调用此函数绘图 """
            x = np.linspace(-3, 5, 30)
            y = x ** 2
            axes = figure.add_subplot(111)
            axes.plot(x, y)

        self.view[0]["plot"] = plot
        super().run()

