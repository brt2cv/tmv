from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    from skimage import morphology
if include("scipy"):
    from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def kernal(size, shape="rect"):
    """ return a np.ndarray as kernal """
    if isinstance(size, np.ndarray):
        return size

    def run_skimage():
        KERNEL_SHAPE_SKIMAGE = {
            "square": morphology.square,  # width
            "rect": morphology.rectangle,  # width, height
            "disk": morphology.disk,  # 圆形: radius
            "ball": morphology.ball,  # 球行: radius
            "diamond": morphology.diamond,  # 钻石形: radius
            "cube": morphology.cube,  # 立方体: width
            "octahedron": morphology.octahedron,  # 八面体: radius
            "octagon": morphology.octagon,  # 八角形: m, n
            "star": morphology.star  # 星形: a
        }
        func_shape = KERNEL_SHAPE_SKIMAGE[shape]
        if isinstance(size, int):
            return func_shape(size)
        else:  # tuple or list
            return func_shape(*size)

    def run_opencv():
        KERNEL_SHAPE_OPENCV = {
            "rect": 0,
            "cross": 1,
            "ellipse": 2
        }
        nShape = KERNEL_SHAPE_OPENCV[shape]
        return cv2.getStructuringElement(nShape, size)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

"""
形态学操作的函数接口中，k参数可以传入两种形式：
* 使用tuple做参数，kernal的形态使用默认的‘rect’形式
* 使用kernal()生成的ndarray，可控制kernal.shape的形态
"""

def dilation(im, k):
    """ 扩充边缘或填充小的孔洞 """
    k = kernal(k)

    def run_opencv():
        return cv2.dilate(im, k)

    def run_skimage():
        return morphology.dilation(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def erosion(im, k):
    """ 常用于提取骨干信息，去掉毛刺，去掉孤立的像素 """
    k = kernal(k)

    def run_opencv():
        return cv2.erode(im, k)

    def run_skimage():
        return morphology.erosion(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def opening(im, k):
    """ 先腐蚀再膨胀，消除小物体或小斑块 """
    k = kernal(k)

    def run_opencv():
        return cv2.morphologyEx(im, cv2.MORPH_OPEN, k)

    def run_skimage():
        return morphology.opening(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def closing(im, k):
    """ 先膨胀再腐蚀，填充孔洞 """
    k = kernal(k)

    def run_opencv():
        return cv2.morphologyEx(im, cv2.MORPH_CLOSE, k)

    def run_skimage():
        return morphology.closing(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()


def gradient(im, k):
    """ 梯度：图像的膨胀和腐蚀之间的差异，结果看起来像目标的轮廓 """
    k = kernal(k)

    def run_opencv():
        return cv2.morphologyEx(im, cv2.MORPH_GRADIENT, k)

    return run_backend(
            func_opencv=run_opencv
        )()


def tophat(im, k):
    """ 顶帽：原图像减去它的开运算值，突出原图像中比周围亮的区域 """
    k = kernal(k)

    def run_opencv():
        return cv2.morphologyEx(im, cv2.MORPH_TOPHAT, k)

    def run_skimage():
        return morphology.white_tophat(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()


def blackhat(im, k):
    """ 黑帽：原图像减去它的闭运算值，突出原图像中比周围暗的区域 """
    k = kernal(k)

    def run_opencv():
        return cv2.morphologyEx(im, cv2.MORPH_BLACKHAT, k)

    def run_skimage():
        return morphology.black_tophat(im, k)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()
