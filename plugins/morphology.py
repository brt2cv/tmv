# from PyQt5.QtWidgets import QMessageBox
from core.plugin.adapter import asFilter, IpyPlugin

def export_plugin(cls: str):
    cls_obj = eval(cls)
    if issubclass(cls_obj, IpyPlugin):
        return asFilter(cls_obj)
    else:
        return cls_obj


import scipy.ndimage as nimg

# from core.plugin import DialogFilter
# class GaussianBlur_A(DialogFilter):
#     """ 使用标准格式定义插件 """
#     title = 'Gaussian Smoothing'

#     def processing(self, im_arr):
#         return nimg.filters.gaussian_filter(im_arr, 1)

class GaussianBlur(IpyPlugin):
    """ 使用适配器定义插件
        只需要修改: class_name、IpyFilter与title
    """
    title = 'Gaussian Smoothing'
    note = ['all', 'auto_msk', 'auto_snap','preview']
    para = {'sigma':2}
    view = [(float, 'sigma', (0,30), 1,  'sigma', 'pix')]

    def run(self, ips, snap, img, para = None):
        nimg.gaussian_filter(snap, para['sigma'], output=img)

class MedianBlur(IpyPlugin):
    title = 'Uniform'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(float, 'size', (0,30), 1,  'size', 'pix')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.uniform_filter(snap, para['size'], output=img)
