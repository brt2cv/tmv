
Backend = "opencv"

if Backend == "pillow":
    pass

elif Backend == "skimage":
    pass

elif Backend == "opencv":
    import cv2

else:
    raise Exception("当前Backend 【{Backend}】 不支持绘图功能")


def threshold(im_arr, thresh, maxval=255, type_=0, otsu=False):
    """ type_:
            cv2.THRESH_BINARY
            cv2.THRESH_BINARY_INV
            cv2.THRESH_TRUNC
            cv2.THRESH_TOZERO
            cv2.THRESH_TOZERO_INV
    """
    if Backend == "pillow":
        pass

    elif Backend == "opencv":
        if otsu and type_ < 8:
            type_ += 8  # cv2.THRESH_OTSU
        ret, im2 = cv2.threshold(im_arr, thresh, maxval, type_)
        return im2

    else:
        print("敬请期待")

    return im2
