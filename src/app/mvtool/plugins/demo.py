from core.plugin import Plugin
from core.plugin.filter import Filter, DialogFilter


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


class DebugForPlugin(DialogFilter):
    title = "App内部Plugin"
    buttons = ["close"]
    view = [{
        "type": "slider",
        "name": "参数  ",
        "val_init": 128,
        "val_range": [0, 255],
        "para": "thresh"
    },{
        "type": "slider",
        "name": "可选参数",
        "val_init": 255,
        "val_range": [0, 255],
        "isCheckbox": True,
        "para": "maxval"
    }]
    # para = {"thresh": 128, "maxval": 255}
    scripts = "{output} = mvlib.filters.threshold({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        print(">>>", self.paras["thresh"], self.paras["maxval"])

    def run(self):
        print("调用App内部插件")
        super().run()


import numpy as np
class MatplotDemo(DialogFilter):
    """ 使用Matplotlib绘制图表 """
    title = "MatplotDemo"
    buttons = ["Close"]
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


from core.plugin.adapter import IpyPlugin
class GaussianBlur(IpyPlugin):
    """ 使用适配器定义插件
        只需要修改: class_name、IpyFilter与title
    """
    title = 'Gaussian Smoothing'
    note = ['all', 'auto_msk', 'auto_snap','preview']
    para = {'sigma':2}
    view = [(float, 'sigma', (0,30), 1,  'sigma', 'pix')]

    def run(self, ips, snap, img, para = None):
        import scipy.ndimage as nimg
        nimg.gaussian_filter(snap, para['sigma'], output=img)
