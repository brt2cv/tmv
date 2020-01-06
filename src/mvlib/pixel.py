from .backend import run_backend, include

if include("opencv"):
    import cv2
# if include("skimage"):
#     import skimage
# if include("scipy"):
#     from scipy import ndimage
if include("numpy"):
    import numpy as np
# if include("pillow"):
#     from PIL import Image


# def blit_copy(img1, img2):
#     img1[:] = img2

# def blit_max(img1, img2):
#     msk = img2>img1
#     img1[msk] = img2[msk]

# def blit_min(img1, img2):
#     msk = img2<img1
#     img1[msk] = img2[msk]

def diff(img1, img2):
    msk = img2>img1
    umsk = True ^ msk
    img1[msk] = img2[msk] - img1[msk]
    img1[umsk] = img1[umsk] - img2[umsk]

def add(img1, img2):
    if img1.dtype == np.uint8:
        msk = img2 > 255-img1
        img1 += img2
        img1[msk] = 255
    else: img1 += img2

def substract(img1, img2):
    if img1.dtype == np.uint8:
        msk = img1<img2
        img1 -= img2
        img1[msk] = 0
    else: img1 -= img2

def multiply(img1, img2):
    pass

def divide(img1, img2):
    pass

def absdiff(img1, img2):
    pass

# def scaleAdd():

# def addWeighted():

def bitwise_and(im_arr, mask):
    """ 取交集 """
    def run_opencv():
        return cv2.bitwise_and(im_arr, im_arr, mask)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def bitwise_diff(im_arr, mask):
    mask_not = bitwise_not(mask)
    return bitwise_and(im_arr, mask_not)

def bitwise_or(im_arr, mask):
    """ 取并集 """
    def run_opencv():
        return cv2.bitwise_or(im_arr, mask)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def bitwise_xor(im_arr, mask):
    """ 取不重叠的区域 """
    def run_opencv():
        return cv2.bitwise_xor(im_arr, mask)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

def bitwise_not(im_arr):
    """ 取反 """
    def run_opencv():
        return cv2.bitwise_not(im_arr)

    return run_backend(
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
            func_opencv=run_opencv
        )()

