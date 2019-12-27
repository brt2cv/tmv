from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    from skimage import transform
if include("scipy"):
    from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


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

def bitwise_add(img1, img2):
    """ 取交集 """

def bitwise_or(img1, img2):
    """ 取并集 """

def bitwise_xor(img1, img2):
    """ 取不重叠的区域 """

def bitwise_not(img1, img2):
    """ 取反 """
