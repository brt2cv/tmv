
Backend = "pillow"

if Backend == "numpy":
    import numpy as np

elif Backend == "pillow":
    from utils.imgio import convert_mode

elif Backend == "skimage":
    from skimage import draw

elif Backend == "opencv":
    import cv2

else:
    raise Exception("当前Backend 【{Backend}】 不支持绘图功能")

def rgb2gray(im_arr):
    if Backend == "numpy":
        weights = np.c_[0.2989, 0.5870, 0.1140]
        # 按照reps指定的次数在相应的维度上重复A矩阵来构建一个新的矩阵
        tile = np.tile(weights, reps=(im_arr.shape[0], im_arr.shape[1], 1))
        return np.sum(tile * im_arr, axis=2)

    elif Backend == "pillow":
        im2 = convert_mode(im_arr, "L")

    else:
        print("敬请期待")
    return im2

# def gray2rgb(im_arr):
#     im2 = im_arr.copy()
#     if Backend == "pillow":
#         pass
#     else:
#         print("敬请期待")
#     return im2
