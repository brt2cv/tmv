from .backend import run_backend, include
from .morphology import kernal

if include("opencv"):
    import cv2
if include("skimage"):
    import skimage
if include("scipy"):
    import scipy.ndimage as nimg
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

def graystairs(im, low_val, high_val):
    def run_numpy():
        im2 = np.subtract(im, low_val, casting="unsafe")
        k = 255 / max(high_val - low_val, 1e-10)
        im2 = np.multiply(im2, k, casting='unsafe').astype("uint8")
        im2[im < low_val] = 0
        im2[im > high_val] = 255
        return im2

    return run_backend(
            func_numpy=run_numpy
        )()

def contrast(im, bright, contrast):
    def run_numpy():
        mid = 128 - bright
        length = 255 / np.tan(contrast / 180 * np.pi)

        im2 = im.copy()
        if mid - length / 2 > 0:
            np.subtract(im2, mid-length / 2, out=im2, casting='unsafe')
            np.multiply(im2, 255 / length, out=im2, casting='unsafe')
        else:
            np.multiply(im2, 255 / length, out=im2, casting='unsafe')
            np.subtract(im2, (mid - length / 2) / length * 255, out=im2, casting='unsafe')
        im2[im < mid-length/2] = 0
        im2[im > mid+length/2] = 255
        return im2

    return run_backend(
            func_numpy=run_numpy
        )()

bright = contrast

#####################################################################
def histogram(im, nBins=256):
    def run_numpy():
        return np.histogram(im, range(0, nBins))[0]

    # def run_skimage():
    #     """ 会自动省略起始和末尾的0列 """
    #     return skimage.exposure.histogram(im, range(0, nBins))

    def run_opencv():
        hist = cv2.calcHist([im],[0],None,[256],[0,255])
        return hist

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            func_numpy=run_numpy
        )()

def _hist_like(hist1, hist2):
    hist1 = np.cumsum(hist1) / hist1.sum()
    hist2 = np.cumsum(hist2) / hist2.sum()
    hist = np.zeros(256, dtype=np.uint8)
    i1, i2 = 0, 0
    while i2 < 256:
        while i1 < 256 and hist2[i2] > hist1[i1]:
            i1 += 1
        hist[i2] = i1
        i2 += 1
    return hist

def hist_normalize(im):
    def run_numpy():
        hist = histogram(im, 257)
        ahist = _hist_like(np.ones(256), hist)
        return ahist[im]

    return run_backend(
            func_numpy=run_numpy
        )()

#####################################################################
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

    def run_scipy():
        return nimg.gaussian_filter(im, sigma)

    def run_skimage():
        return skimage.filters.gaussian(im, sigma)

    return run_backend(
            func_opencv=run_opencv,
            func_scipy=run_scipy,
            func_skimage=run_skimage
        )()

def median(im, k: int):
    def run_opencv():
        """ k: 必须为奇数 """
        k_val = k if k % 2 else k+1
        return cv2.medianBlur(im, k_val)

    def run_scipy():
        return nimg.median_filter(im, k)

    def run_skimage():
        if isinstance(k, int):
            k_nal = kernal(k, "square")
        else:
            k_nal = kernal(k)
        return skimage.filters.median(im, k_nal)

    return run_backend(
            func_opencv=run_opencv,
            func_scipy=run_scipy,
            func_skimage=run_skimage
        )()

def mean(im, k: tuple):
    def run_opencv():
        return cv2.blur(im, k)

    def run_scipy():
        return nimg.uniform_filter(im, k)

    return run_backend(
            func_opencv=run_opencv,
            func_scipy=run_scipy
        )()

# def filter2D(im, k):
#     def run_opencv(ksize):
#         return cv2.filter2D(im, -1, ksize)

#     return run_backend(
#             func_opencv=run_opencv
#         )()

# def laplace(im, uniform=False):
#     def run_scipy():
#         im2 = nimg.laplace(im)
#         im2 *= -1
#         if uniform:
#             im2 = np.add(im2, np.mean(ips.range))
#         return im2

#     return run_backend(
#             # func_opencv=run_opencv,
#             func_scipy=run_scipy
#         )()

# def DOG(im, sigma, sigma2, uniform=False):

# def gaussian_laplace(im, sigma, uniform=False):
#     def run_scipy():
#         im2 = nimg.gaussian_laplace(im, sigma)
#         im2 *= -1
#         if uniform:
#             im2 = np.add(im2, np.mean(ips.range))
#         return im2

#     return run_backend(
#             # func_opencv=run_opencv,
#             func_scipy=run_scipy
#         )()

def maximum(im, k):
    """ k: int or tuple """
    def run_scipy():
        return nimg.maximum_filter(im, k)

    return run_backend(
            # func_opencv=run_opencv,
            func_scipy=run_scipy
        )()

def minimum(im, k):
    """ k: int or tuple """
    def run_scipy():
        return nimg.minimum_filter(im, k)

    return run_backend(
            # func_opencv=run_opencv,
            func_scipy=run_scipy
        )()

def percentile(im, k):
    def run_scipy():
        return nimg.percentile_filter(im, k)

    return run_backend(
            # func_opencv=run_opencv,
            func_scipy=run_scipy
        )()

def prewitt(im, axis: int):
    orientation = {'horizontal':0, 'vertical':1}
    if isinstance(axis, str):
        axis = orientation[axis]

    def run_scipy():
        return nimg.prewitt(im, axis)

    return run_backend(
            # func_opencv=run_opencv,
            func_scipy=run_scipy
        )()

def sobel(im, axis: int):
    orientation = {'horizontal':0, 'vertical':1, "both":2}
    if isinstance(axis, str):
        axis = orientation[axis]

    def run_scipy():
        if axis == 2:
            im_ = im + np.abs(nimg.sobel(im, 0))
            im2 = im_ + np.abs(nimg.sobel(im_, 1))
        else:
            im2 = np.abs(nimg.sobel(im, axis))
        return im2 // 4

    return run_backend(
            # func_opencv=run_opencv,
            func_scipy=run_scipy
        )()
