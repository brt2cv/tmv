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


# def asFilter(IpyPlugClass):
#     """ return a class of PluginAdapter4Ipy """
#     filter_plugin = PluginAdapter4Ipy(IpyPlugClass)
#     return filter_plugin


from .. import g
class PluginAdapter4Ipy(DialogFilter):
    def __init__(self, ipy_plug_cls):
        self.proxy = ipy_plug_cls  # IpyPlugin class
        self.title = ipy_plug_cls.title
        self.note2features()
        self.setup_tpl_widgets()
        super().__init__(g.get("mwnd"))

    def note2features(self):
        note = self.proxy.note  # list
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

        self.features = features

    def setup_tpl_widgets(self):
        self.view = []
        for tuple_info in self.proxy.view:
            dict_wx = {"isCheckbox": False}
            ctrl, para, val_range, _, name, _unit = tuple_info
            # widgets = { 'ctrl':None, 'slide':FloatSlider, int:NumCtrl, 'path':PathCtrl,
            #             float:NumCtrl, 'lab':Label, bool:Check, str:TextCtrl,
            #             list:Choice, 'img':ImageList, 'tab':TableList, 'color':ColorCtrl,
            #             'any':AnyType, 'chos':Choices, 'fields':TableFields,
            #             'field':TableField, 'hist':HistCanvas, 'cmap':ColorMap}
            wx2ctrls = {
                "edit": [float],
                "spinbox": [int],
                "slider": ["slide"],
                "radio": [list]
            }
            for wx_name, ctrls in wx2ctrls.items():
                if ctrl in ctrls:
                    dict_wx["type"] = wx_name
                    break
            dict_wx["name"] = name
            dict_wx["val_range"] = val_range
            dict_wx["val_init"] = self.proxy.para[para]
            dict_wx["para"] = para

            self.view.append(dict_wx)

    def processing(self, im_arr):
        import numpy as np
        output = np.zeros(im_arr.shape, dtype=np.uint8)
        self.proxy.run(self=None,
                       ips=None,
                       snap=im_arr,  # src
                       img=output,   # dst
                       para=self.para)
        return output
