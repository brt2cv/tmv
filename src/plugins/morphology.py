import numpy as np
import scipy.ndimage as nimg
import mvlib

from core.plugin.filter import DialogFilter
from core.plugin.adapter import IpyPlugin as Filter


class GaussianBlur(DialogFilter):
    """ 使用适配器定义插件
        只需要修改: class_name、IpyFilter与title
    """
    title = 'Gaussian Smoothing'
    view = [{
        "type": "slider",
        "name": "sigma_x ",
        "val_init": 2,
        "val_range": [1, 29],
        "para": "sigma_x"
    },{
        "type": "slider",
        "name": "sigma_y ",
        "val_init": 2,
        "val_range": [1, 29],
        "isCheckbox": True,
        "para": "sigma_y"
    }]
    scripts = "{output} = mvlib.filters.gaussian({im}, {sigma})"

    def processing(self, im_arr):
        self.paras["sigma"] = (self.paras["sigma_x"],
                               self.paras["sigma_y"])
        return mvlib.filters.gaussian(im_arr, self.paras['sigma'])

class MedianBlur(DialogFilter):
    title = 'Median Smoothing'
    view = [{
        "type": "slider",
        "name": "ksize ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "ksize"
    }]
    scripts = "{output} = mvlib.filters.median({im}, {ksize})"

    def processing(self, im_arr):
        # kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.filters.median(im_arr, self.paras["ksize"])

class MeanBlur(DialogFilter):
    title = 'Mean Smoothing'
    view = [{
        "type": "slider",
        "name": "kernal-width  ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_w"
    },{
        "type": "slider",
        "name": "kernal-height ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_h"
    }]
    scripts = "{output} = mvlib.filters.mean({im}, ({k_w}, {k_h}))"

    def processing(self, im_arr):
        kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.filters.mean(im_arr, kernal)

class Erosion(DialogFilter):
    title = "Erosion"
    view = [{
        "type": "spinbox",
        "name": "kernal-width  ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_w"
    },{
        "type": "spinbox",
        "name": "kernal-height ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_h"
    }]
    scripts = "{output} = mvlib.morphology.erosion({im}, ({k_w}, {k_h}))"

    def processing(self, im_arr):
        kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.morphology.erosion(im_arr, kernal)

class Dilation(DialogFilter):
    title = "Dilation"
    view = [{
        "type": "spinbox",
        "name": "kernal-width  ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_w"
    },{
        "type": "spinbox",
        "name": "kernal-height ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_h"
    }]
    scripts = "{output} = mvlib.morphology.dilation({im}, ({k_w}, {k_h}))"

    def processing(self, im_arr):
        kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.morphology.dilation(im_arr, kernal)

class Opening(DialogFilter):
    title = "Opening"
    view = [{
        "type": "spinbox",
        "name": "kernal-width  ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_w"
    },{
        "type": "spinbox",
        "name": "kernal-height ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_h"
    }]
    scripts = "{output} = mvlib.morphology.opening({im}, ({k_w}, {k_h}))"

    def processing(self, im_arr):
        kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.morphology.opening(im_arr, kernal)

class Closing(DialogFilter):
    title = "Closing"
    view = [{
        "type": "spinbox",
        "name": "kernal-width  ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_w"
    },{
        "type": "spinbox",
        "name": "kernal-height ",
        "val_init": 3,
        "val_range": [1, 29],
        "para": "k_h"
    }]
    scripts = "{output} = mvlib.morphology.closing({im}, ({k_w}, {k_h}))"

    def processing(self, im_arr):
        kernal = (self.paras["k_w"], self.paras["k_h"])
        return mvlib.morphology.closing(im_arr, kernal)

#####################################################################

class GaussianLaplaceBlur(Filter):
    title = 'Gaussian Laplace'
    note = ['all', '2int',  'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'sigma':2, 'uniform':False}
    view = [(float, 'sigma', (0,30), 1,  'sigma', 'pix'),
            (bool, 'uniform', 'uniform')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.gaussian_laplace(snap, para['sigma'], output=img)
        img *= -1
        if para['uniform']: np.add(img, np.mean(ips.range), out=img, casting='unsafe')

class DoG(Filter):
    title = 'Difference of Gaussian'
    note = ['all', 'auto_msk', 'auto_snap', '2int', 'preview']

    #parameter
    para = {'sigma1':0, 'sigma2':2, 'uniform':False}
    view = [(float, 'sigma1', (0,30), 1,  'sigma1', 'pix'),
            (float, 'sigma2', (0,30), 1,  'sigma2', ''),
            (bool, 'uniform', 'uniform')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.gaussian_filter(snap, para['sigma1'], output=img)
        buf = nimg.gaussian_filter(snap, para['sigma2'], output=img.dtype)
        img -= buf
        if para['uniform']: np.add(img, np.mean(ips.range), out=img, casting='unsafe')

class Laplace(Filter):
    title = 'Laplace'
    note = ['all', '2int', 'auto_msk', 'auto_snap','preview']

    para = {'uniform':False}
    view = [(bool, 'uniform', 'uniform')]
    #process
    def run(self, ips, snap, img, para = None):
        nimg.laplace(snap, output=img)
        img *= -1
        if para['uniform']: np.add(img, np.mean(ips.range), out=img, casting='unsafe')

class Maximum(Filter):
    title = 'Maximum'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(float, 'size', (0,30), 1,  'size', 'pix')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.maximum_filter(snap, para['size'], output=img)

class Minimum(Filter):
    title = 'Minimum'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(float, 'size', (0,30), 1,  'size', 'pix')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.minimum_filter(snap, para['size'], output=img)

class Percent(Filter):
    title = 'Percent'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2, 'per':50}
    view = [(int, 'size', (0,30), 0, 'size', 'pix'),
            (int, 'per',  (0,100), 0, 'percent', '')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.percentile_filter(snap, para['per'], para['size'], output=img)

class Prewitt(Filter):
    title = 'Prewitt'
    note = ['all', '2int', 'auto_msk', 'auto_snap','preview']
    para = {'axis':'both'}
    view = [(list, 'axis', ['both', 'horizontal', 'vertical'], str, 'direction', 'aixs')]

    #process
    def run(self, ips, snap, img, para = None):
        if para['axis']=='both':
            img[:] =  np.abs(nimg.prewitt(snap, axis=0, output=img.dtype))
            img += np.abs( nimg.prewitt(snap, axis=1, output=img.dtype))
        else:
            nimg.prewitt(snap, axis={'horizontal':0,'vertical':1}[para['axis']], output=img)
            img[:] = np.abs(img)
        img //= 3

class Sobel(Filter):
    title = 'Sobel'
    note = ['all', '2int', 'auto_msk', 'auto_snap','preview']
    para = {'axis':'both'}
    view = [(list, 'axis', ['both', 'horizontal', 'vertical'], str, 'direction', 'aixs')]
    #process
    def run(self, ips, snap, img, para = None):
        if para['axis']=='both':
            img[:] =  np.abs(nimg.sobel(snap, axis=0, output=img.dtype))
            img += np.abs( nimg.sobel(snap, axis=1, output=img.dtype))
        else:
            nimg.sobel(snap, axis={'horizontal':0,'vertical':1}[para['axis']], output=img)
            img[:] = np.abs(img)
        img //= 4

class LaplaceSharp(Filter):
    title = 'Laplace Sharp'
    note = ['all', '2int', 'auto_msk', 'auto_snap','preview']

    para = {'weight':0.2}
    view = [(float, 'weight', (0,5), 1,  'weight', 'factor')]
    #process
    def run(self, ips, snap, img, para = None):
        nimg.laplace(snap, output=img)
        np.multiply(img, -para['weight'], out=img, casting='unsafe')
        img += snap

class Variance(Filter):
    title = 'Variance'
    note = ['all', 'auto_msk', '2float', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(float, 'size', (0,30), 1,  'size', 'pix')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.uniform_filter(snap**2, para['size'], output=img)
        img -= nimg.uniform_filter(snap, para['size'])**2

class USM(Filter):
    title = 'Unsharp Mask'
    note = ['all', 'auto_msk', 'auto_snap', '2int', 'preview']

    #parameter
    para = {'sigma':2, 'weight':0.5}
    view = [(float, 'sigma', (0,30), 1,  'sigma', 'pix'),
            (float, 'weight', (0,5), 1,  'weight', '')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.gaussian_filter(snap, para['sigma'], output=img)
        img -= snap
        np.multiply(img, -para['weight'], out=img, casting='unsafe')
        img += snap
