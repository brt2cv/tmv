import numpy as np
from imageio.core.util import Array, asarray

from .contours import find_cnts, cnts2img
from .color import gray2rgb


def make_rgb(rgb: tuple, w, h):
    assert len(rgb) == 3, f"无法识别的背景色: 【{rgb}】"
    im_arr = np.zeros([h, w, 3], dtype=np.uint8)
    im_arr[..., ] = rgb
    return im_arr

def shape2size(shape):
    """ im_arr.shape: {h, w, c}
        PIL.Image.size: {w, h}
    """
    size = (shape[1], shape[0])
    return size

def shape2mode(shape):
    if len(shape) < 3:
        return "L"
    elif shape[2] == 3:
        return "RGB"  # 无法区分BGR (OpenCV)
    elif shape[2] == 4:
        return "RGBA"
    else:
        raise Exception("未知的图像类型")

def get_mode(im_arr):
    """ 一种预测图像mode的简单方式 """
    if im_arr.ndim < 3:
        return "L"

    shape = im_arr.shape
    if shape[2] == 3:
        return "RGB"  # 无法区分BGR (OpenCV)
    elif shape[2] == 4:
        return "RGBA"
    else:
        raise Exception("未知的图像类型")


class ImagePlus(Array):
    """ ArrayPlus(array, meta=None)

    A subclass of np.ndarray that has a meta attribute. Get the dictionary
    that contains the meta data using ``im.meta``. Convert to a plain numpy
    array using ``np.asarray(im)``.

    """
    # def __new__(cls, array, meta=None):
    #     # Check
    #     if not isinstance(array, np.ndarray):
    #         raise ValueError("Array expects a numpy array.")
    #     if not (meta is None or isinstance(meta, dict)):
    #         raise ValueError("Array expects meta data to be a dict.")
    #     # Convert and return
    #     meta = meta if meta is not None else {}
    #     try:
    #         ob = array.view(cls)
    #     except AttributeError:  # pragma: no cover
    #         # Just return the original; no metadata on the array in Pypy!
    #         return array
    #     ob._copy_meta(meta)
    #     return ob

    def __init__(self, array, meta=None):
        def declare_member(name, value=None):
            if name not in self._meta:
                self._meta[name] = value
        # declare_member("snap", asarray(self).copy())
        declare_member("roi")
        declare_member("mask")  # 由选区自动生成
        declare_member("cnts", [])

    def _copy_meta(self, meta):
        """ Make a 2-level deep copy of the meta dictionary.
        """
        # self._meta = Dict()
        # for key, val in meta.items():
        #     if isinstance(val, dict):
        #         val = Dict(val)  # Copy this level
        #     self._meta[key] = val
        self._meta = meta

    @property
    def mode(self):
        return get_mode(self)

    # def get_msk(self, mode='in'):
    #     if self.roi==None:return None
    #     if self.msk is None:
    #         self.msk = np.zeros(self.size, dtype=np.bool)
    #     if self.roi.update or mode!=self.mskmode:
    #         self.msk[:] = 0
    #         if isinstance(mode, int):
    #             self.roi.sketch(self.msk, w=mode, color=True)
    #         else: self.roi.fill(self.msk, color=True)
    #         if mode=='out':self.msk^=True
    #         self.roi.update = False
    #         self.mskmode=mode
    #     return self.msk

    def find_cnts(self, a, b):
        self.cnts = find_cnts(self, a, b)
        return self.cnts

    def show_cnts(self, bkg=None, color=(0, 0, 0), thinckness=2):
        """ return a new np.ndarray object, with RGB color.
            bkg:
                * None: 默认使用当前图像作为背景
                * 0: 同样size的黑色背景
                * 255: 同样size的白色背景
                * [r, g, b]: 同样size的任意背景
                * im_arr: 任意的图像(可能与self.size不同，导致cnts失效)
        """
        assert self.cnts is not None, "不存在轮廓"

        if bkg is None:
            if self.mode == "L":
                bkg = gray2rgb(self)
            else:
                bkg = self.copy()
        elif not isinstance(bkg, np.ndarray):
            h, w = self.shape[:2]
            if bkg == 0:
                bkg = np.zeros([h, w, 3], np.uint8)
            elif bkg == 255:
                bkg = np.zeros([h, w, 3], np.uint8) + 255
            else:
                bkg = make_rgb(bkg, w, h)

        im2 = cnts2img(self.cnts, bkg, color, thinckness)
        return im2


if __name__ == "__main__":
    im = np.zeros([3, 4])
    ips = ImagePlus(im, {"a":123, "b":234})

    # 经过asarray()后的im，丢失meta属性，类型恢复为
    im2 = asarray(ips)
    print(">> type of asarray(ips): ", type(im2))

    # 简单的np.ndarray操作也会替换源对象
    ips2 = ips.reshape([4,3])
    print(">> type of ips2: ", type(ips2))  # ImagePlus

    ips[0][0] = 1
    print("ips.view: ", ips)
    print("ips.meta: ", ips._meta)

    # copy()操作依旧可用
    ips3 = ips.copy()
    print(">> type of ips3: ", type(ips3))  # ImagePlus
    print(ips3.meta)  # 但不会复制内容，如丢失cnts数据 ??
