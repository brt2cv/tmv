# 用于转换ImagePy的插件为我所用
from .filter import Plugin, DialogFilter

class IpyPlugin(Plugin):
    title = 'Gaussian'
    note = []  # ['all', 'auto_msk', 'auto_snap','preview']
    para = {}  # {'sigma':2}
    view = []  # [(float, 'sigma', (0,30), 1,  'sigma', 'pix')]

    def run(self, ips, snap, img, para = None):
        """ 图像处理函数 """
        # nimg.gaussian_filter(snap, para['sigma'], output=img)


class PluginAdapter4Ipy(DialogFilter):
    proxy = None  # IpyPlugin class

    def __init__(self, parent):
        super().__init__(parent)
        self.title = self.proxy.title
        self.features = self.note2features(self.proxy.note)
        self.setup_tpl_widgets()

    def note2features(self, note: list):
        features = {}
        def conflict_check(key, value):
            if key in features:
                raise Exception(f"属性冲突: 已存在【{features[key]}】，新添加【{value}】")

        if "rgb" in note:
            conflict_check("mode", "rgb")
        if "not_channel" in note:
            conflict_check("mode", "gray")

        if "8-bit" in note:
            conflict_check("dtype", "uint8")
        if "16-bit" in note:
            conflict_check("dtype", "uint16")
        if "int" in note:
            conflict_check("dtype", "uint32")
        if "float" in note:
            conflict_check("dtype", "float")

        return features

    def processing(self, im_arr):
        import numpy as np
        output = np.zeros(im_arr.shape, dtype=np.uint8)
        self.proxy.run(self=None,
                       ips=None,
                       snap=im_arr,  # src
                       img=output,   # dst
                       para=self.proxy.para)
        return output

    def setup_tpl_widgets(self):
        for tuple_info in self.proxy.view:
            pass




def asFilter(IpyPlugin):
    """ return a class of PluginAdapter4Ipy """
    cls = PluginAdapter4Ipy
    cls.proxy = IpyPlugin
    return cls


if __name__ == "__main__":
    import scipy.ndimage as nimg
    from core.plugin.adapter import asFilter, IpyPlugin as Filter

    class GaussianBlur(Filter):
        """ 使用适配器定义插件
            只需要修改: class_name、IpyFilter与title
        """
        title = 'Gaussian Smoothing'
        note = ['all', 'auto_msk', 'auto_snap','preview']
        para = {'sigma':2}
        view = [(float, 'sigma', (0,30), 1,  'sigma', 'pix')]

        def run(self, ips, snap, img, para = None):
            nimg.gaussian_filter(snap, para['sigma'], output=img)
