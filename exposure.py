from .backend import run_backend, include

# if include("opencv"):
#     import cv2
if include("skimage"):
    import skimage
# if include("scipy"):
#     from scipy import ndimage
if include("numpy"):
    import numpy as np
# if include("pillow"):
#     from PIL import Image


def histogram(im, nBins=256):
    def run_numpy():
        return np.histogram(im, nBins)

    def run_skimage():
        return skimage.exposure.histogram(nBins)

    return run_backend(
            func_skimage=run_skimage,
            # func_opencv=run_opencv,
            func_numpy=run_numpy
        )()
