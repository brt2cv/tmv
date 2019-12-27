from .backend import run_backend, include

if include("opencv"):
    import cv2
# if include("skimage"):
#     from skimage import *
if include("scipy"):
    from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def rgb2gray(im):
    def run_opencv():
        return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    def run_numpy():
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

