import cv2

KERNEL_SHAPE = {
    "rect": 0,
    "cross": 1,
    "ellipse": 2
}

# make_kernel = cv2.getStructuringElement
def kernel(esize: tuple, shape="rect"):
    shape = KERNEL_SHAPE[shape]
    kernel = cv2.getStructuringElement(shape, esize)
    return kernel

erosion = cv2.erode

dilation = cv2.dilate

def opening(img, kernel):
    opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return opening

def closing(img, kernel):
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return closing

def gradient(img, kernel):
    """ 梯度：图像的膨胀和腐蚀之间的差异，结果看起来像目标的轮廓 """
    gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
    return gradient

def tophat(img, kernel):
    """ 顶帽：原图像与开运算图的区别，突出原图像中比周围亮的区域 """
    tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
    return tophat

def blackhat(img, kernel):
    """ 黑帽：原图像与闭运算图的区别，突出原图像中比周围暗的区域 """
    blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)
    return blackhat

##############################################################################

def blur_Gaussian(img, ksize=(5, 5), sigma=0):
    for x in ksize:
        if not isinstance(x, int):
            print("高斯内核需要为整数")
            return
        if x <= 0:
            print("高斯内核需要为正数")
            return
        if x % 2 == 0:
            print("高斯内核需要为奇数")
            return

    blur = cv2.GaussianBlur(img, ksize, sigma)
    return blur

def blur_median(img, ksize=5):
    blur = cv2.medianBlur(img, ksize)
    return blur

def blur_filter2D(img, ksize):
    blur = cv2.filter2D(img, -1, ksize)
    return blur

def blur_average(img, ksize=(3,5)):
    blur = cv2.blur(img, ksize)
    return blur
