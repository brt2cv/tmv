import numpy as np
import scipy.ndimage as nimg
from core.plugin.adapter import IpyPlugin as Filter

# from core.plugin.filter import DialogFilter
# class GaussianBlur_A(DialogFilter):
#     """ 使用标准格式定义插件 """
#     title = 'Gaussian Smoothing'

#     def processing(self, im_arr):
#         return nimg.filters.gaussian_filter(im_arr, 1)

class MedianBlur(Filter):
    title = 'Median Smoothing'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(int, 'size', (0,30), 0,  'size', 'pix')]

    scripts = "{output} = mvlib.filters.median({im}, {size})"

    #process
    def run(self, ips, snap, img, para = None):
        nimg.median_filter(snap, para['size'], output=img)


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


class MeanBlur(Filter):
    title = 'Median Smoothing'
    note = ['all', 'auto_msk', 'auto_snap','preview']

    #parameter
    para = {'size':2}
    view = [(float, 'size', (0,30), 1,  'size', 'pix')]

    #process
    def run(self, ips, snap, img, para = None):
        nimg.uniform_filter(snap, para['size'], output=img)


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
