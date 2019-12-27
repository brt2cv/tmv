from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    from skimage import feature
if include("scipy"):
    from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def canny(im, sigma=1.):
    def run_skimage():
        return feature.canny(im, sigma)

    def run_opencv(thresh1, thresh2):
        return cv2.canny(im, thresh1, thresh2)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()
