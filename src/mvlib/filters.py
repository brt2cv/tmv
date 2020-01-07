from .backend import run_backend, include
from .morphology import kernal

if include("opencv"):
    import cv2
if include("skimage"):
    import skimage
# if include("scipy"):
#     from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def threshold(im, thresh="otsu", maxval=255):
    """ thresh could be a int for threshold, or string for a method of auto-type """
    # method = thresh is isinstance(thresh, str) else None
    # thresh = thresh if method is None else 0
    params = {"thresh": thresh}  # 用于函数内修改阈值

    def run_numpy():
        thresh = params["thresh"]  # 用于更新otsu阈值

        if maxval == 255:
            im2 = ((im < thresh) * 255).astype("uint8")
        else:
            im2 = np.zeros(im.shape, dtype="uint8")
            im2[im > maxval] = 255
            im2[im < thresh] = 255
        return im2

    def run_skimage():
        """ 当重新向thresh赋值时报错：
            `NameError: name 'thresh' is not defined`
            使用 `global thresh` 未能解决
        """
        if thresh == "otsu":
            params["thresh"] = skimage.filters.threshold_otsu(im)
        elif thresh in ["isodata", "yen", "li", "local", "minimum"]:
            raise Exception("尚未支持的自动阈值方法，敬请期待")
        return run_numpy()

    def run_opencv():
        """ type_:
                cv2.THRESH_BINARY
                cv2.THRESH_BINARY_INV
                cv2.THRESH_TRUNC
                cv2.THRESH_TOZERO
                cv2.THRESH_TOZERO_INV
        """
        type_ = cv2.THRESH_BINARY  # 0
        if thresh == "otsu":
            type_ += cv2.THRESH_OTSU  # 8
            params["thresh"] = 0

        _ret, im2 = cv2.threshold(im, params["thresh"], maxval, type_)
        return im2

    def run_pillow():
        # return im.convert("1")  # 阈值为127
        if maxval == 255:
            return im.point(lambda i: i < thresh and 255)
        else:
            middle = maxval - thresh + 1
            mask = [0] * thresh + [1] * middle + [0] * (255 - maxval)
            return im.point(mask, "1")

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv,
            func_pillow=run_pillow,
            func_numpy=run_numpy
        )()


def gaussian(im, sigma):
    """
    sigma: scalar or sequence of scalars
    """
    def run_opencv():
        """
        ksize.width和ksize.height必须为正数和奇数，也可以为零，然后根据sigma计算得出
        sigmas可以为零，则分别从ksize.width和ksize.height计算得出
        """
        if isinstance(sigma, int):
            sigma_x = sigma_y = sigma
        else:
            sigma_x, sigma_y = sigma
        return cv2.GaussianBlur(im, None, sigma_x, sigmaY=sigma_y)

    def run_skimage():
        return skimage.filters.gaussian(im, sigma)

    return run_backend(
            func_opencv=run_opencv,
            func_skimage=run_skimage
        )()

def median(im, k: int):
    def run_opencv():
        """ k: 必须为奇数 """
        k_val = k if k % 2 else k+1
        return cv2.medianBlur(im, k_val)

    def run_skimage():
        k_nal = kernal(k, "square")  # 功能被限制了……
        return skimage.filters.median(im, k_nal)

    return run_backend(
            func_opencv=run_opencv,
            func_skimage=run_skimage
        )()

def mean(im, k: tuple):
    def run_opencv():
        return cv2.blur(im, k)

    return run_backend(
            func_opencv=run_opencv
        )()

def filter2D(im, k):
    def run_opencv(ksize):
        return cv2.filter2D(im, -1, ksize)

    return run_backend(
            func_opencv=run_opencv
        )()
