from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    import skimage
    from .io import float2ubyte
# if include("scipy"):
#     from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def rgb2gray(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    def run_numpy():
        # return np.dot(im[..., :3], [0.299, 0.587, 0.144])
        weights = np.c_[0.2989, 0.5870, 0.1140]
        # 按照reps指定的次数在相应的维度上重复A矩阵来构建一个新的矩阵
        tile = np.tile(weights, reps=(im.shape[0], im.shape[1], 1))
        return np.sum(tile * im, axis=2, dtype=im.dtype)

    def run_pillow():
        return im.convert("L")

    return run_backend(
            func_pillow=run_pillow,
            func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def gray2rgb(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)

    return run_backend(
            func_opencv=run_opencv
        )()

def rgb2bgr(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

    def run_numpy():
        r, g, b = split(im)
        return merge([b, g, r])

    return run_backend(
            func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def bgr2rgb(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    def run_numpy():
        b, g, r = split(im)
        return merge([r, g, b])

    return run_backend(
            func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def split(im):
    def run_pillow():
        # im.getchannel()
        return im.split()

    def run_numpy():
        assert im.ndim >= 3, "无法分离单通道图像"
        channels = []
        for index in range(im.shape[2]):
            channel = im[:,:,index]
            channels.append(channel)
        return channels

    def run_opencv():
        return cv2.split(im)

    return run_backend(
            func_pillow=run_pillow,
            func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def merge(bands):
    def run_pillow():
        return Image.merge(mode, bands)

    def run_numpy():
        shape = bands[0].shape
        ret = np.zeros([*shape, len(bands)], dtype=np.uint8)
        for index, band in enumerate(bands):
            assert shape == band.shape, "bands.shape不一致，无法merge"
            ret[:,:,index] = band
        return ret

    def run_opencv():
        return cv2.merge(bands)

    return run_backend(
            func_pillow=run_pillow,
            func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

#####################################################################
def _BGR2HSV(_img):
# https://github.com/gzr2017/ImageProcessing100Wen/blob/master/Question_01_10/answers_py/answer_5.py
    im = _img.copy() / 255.
    hsv = np.zeros_like(im, dtype=np.float32)

    # get max and min
    max_v = np.max(im, axis=2).copy()
    min_v = np.min(im, axis=2).copy()
    min_arg = np.argmin(im, axis=2)

    # H
    hsv[..., 0][np.where(max_v == min_v)] = 0
    ## if min == B
    ind = np.where(min_arg == 0)
    hsv[..., 0][ind] = 60 * (im[..., 1][ind] - im[..., 2][ind]) / (max_v[ind] - min_v[ind]) + 60
    ## if min == R
    ind = np.where(min_arg == 2)
    hsv[..., 0][ind] = 60 * (im[..., 0][ind] - im[..., 1][ind]) / (max_v[ind] - min_v[ind]) + 180
    ## if min == G
    ind = np.where(min_arg == 1)
    hsv[..., 0][ind] = 60 * (im[..., 2][ind] - im[..., 0][ind]) / (max_v[ind] - min_v[ind]) + 300

    # S
    hsv[..., 1] = max_v.copy() - min_v.copy()

    # V
    hsv[..., 2] = max_v.copy()
    return hsv

def _HSV2BGR(_img, hsv):
# https://github.com/gzr2017/ImageProcessing100Wen/blob/master/Question_01_10/answers_py/answer_5.py
    im = _img.copy() / 255.

    # get max and min
    max_v = np.max(im, axis=2).copy()
    min_v = np.min(im, axis=2).copy()

    H = hsv[..., 0]
    S = hsv[..., 1]
    V = hsv[..., 2]

    C = S
    H_ = H / 60.
    X = C * (1 - np.abs( H_ % 2 - 1))
    Z = np.zeros_like(H)

    vals = [[Z,X,C], [Z,C,X], [X,C,Z], [C,X,Z], [C,Z,X], [X,Z,C]]
    out = np.zeros_like(im)
    for i in range(6):
        ind = np.where((i <= H_) & (H_ < (i+1)))
        out[..., 0][ind] = (V - C)[ind] + vals[i][0][ind]
        out[..., 1][ind] = (V - C)[ind] + vals[i][1][ind]
        out[..., 2][ind] = (V - C)[ind] + vals[i][2][ind]

    out[np.where(max_v == min_v)] = 0
    out = np.clip(out, 0, 1)
    out = (out * 255).astype(np.uint8)
    return out

# ============= RGB - HSV ============
def rgb2hsv(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # def run_numpy():
    #     im_hsv = _BGR2HSV(im)
    #     im_hsv[..., 0] = (im_hsv[..., 0] + 180) % 360
    #     return im_hsv

    def run_skimage():
        im_float = skimage.color.rgb2hsv(im)
        return float2ubyte(im_float)

    return run_backend(
            # func_pillow=run_pillow,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def hsv2rgb(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_HSV2BGR)

    def run_skimage():
        im_float = skimage.color.hsv2rgb(im)
        return float2ubyte(im_float)

    return run_backend(
            # func_pillow=run_pillow,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

hsv_color = {  # ["hmin", "hmax", "smin", "smax", "vmin", "vmax"]
    "black": [0, 180, 0, 255, 0, 46],
    "gray": [0, 180, 0, 43, 46, 220],
    "white": [0, 180, 0, 30, 221, 255],
    "red": [156, 10, 43, 255, 46, 255],
    "orange": [11, 25, 43, 255, 46, 255],
    "yellow": [26, 34, 43, 255, 46, 255],
    "green": [35, 77, 43, 255, 46, 255],
    "cyan": [78, 99, 43, 255, 46, 255],
    "blue": [100, 124, 43, 255, 46, 255],
    "purple": [125, 155, 43, 255, 46, 255],
}

def hsv_range(img_hsv, color_range):
    """ color_range: [156, 10, 43, 255, 46, 255], 也支持使用预定义色值: "red", "black"
    """
    if isinstance(color_range, str):
        color_range = hsv_color[color_range]

    def run_opencv():
        array_low = np.array([v for i, v in enumerate(color_range) if i % 2 == 0])
        array_high = np.array([v for i, v in enumerate(color_range) if i % 2])

        if array_low[0] <= array_high[0]:
            mask = cv2.inRange(img_hsv, array_low, array_high)
        else:
            array_low_0 = array_low.copy()
            array_low_0[0] = 0
            array_high_180 = array_high.copy()
            array_high_180[0] = 180
            mask0 = cv2.inRange(img_hsv, array_low, array_high_180)
            mask1 = cv2.inRange(img_hsv, array_low_0, array_high)
            mask = cv2.add(mask0, mask1)
        return mask

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

# ============= RGB - Lab ============
def rgb2lab(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2LAB)

    def run_skimage():
        rst = skimage.color.rgb2lab(im)
        print('============', rst.min(), rst.max())
        return ((rst + 100) * (255 / 200)).astype(np.uint8)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def lab2rgb(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_Lab2BGR)

    def run_skimage():
        rst = im * (200 / 255) - 100
        rst = skimage.color.lab2rgb(rst)
        return (rst * 255).astype(np.uint8)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

# ============= RGB - YUV ============
def rgb2yuv(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2YUV)

    def run_skimage():
        rst = skimage.color.rgb2yuv(im)
        print('============', rst.min(), rst.max())
        return float2ubyte(rst)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def yuv2rgb(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_YUV2BGR)

    def run_skimage():
        rst = skimage.color.yuv2rgb(im)
        print('============', rst.min(), rst.max())
        return float2ubyte(rst)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

# ============= RGB - XYZ ============
def rgb2xyz(im):
    def run_skimage():
        rst = skimage.color.rgb2xyz(im)
        # print('============', rst.min(), rst.max())
        return (rst*(200)).astype(np.uint8)

    return run_backend(
            func_skimage=run_skimage
        )()

def xyz2rgb(im):
    def run_skimage():
        rst = skimage.color.xyz2rgb(im / 200)
        # print('============', rst.min(), rst.max())
        return float2ubyte(rst)

    return run_backend(
            func_skimage=run_skimage
        )()
