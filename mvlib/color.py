
Backend = "pillow"

if Backend == "pillow":
    from util.imgio import convert_mode

elif Backend == "skimage":
    from skimage import draw

elif Backend == "opencv":
    import cv2

else:
    raise Exception("当前Backend 【{Backend}】 不支持绘图功能")

def rgb2gray(im_arr):
    if Backend == "pillow":
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
