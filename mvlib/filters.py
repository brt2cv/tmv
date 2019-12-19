
Backend = "numpy"

if Backend == "numpy":
    import numpy as np

elif Backend == "pillow":
    pass

elif Backend == "skimage":
    pass

elif Backend == "opencv":
    import cv2

else:
    raise Exception("当前Backend 【{Backend}】 不支持绘图功能")


def threshold(im_arr, thresh, maxval=255, otsu=False):
    if Backend == "opencv":
        """ type_:
                cv2.THRESH_BINARY
                cv2.THRESH_BINARY_INV
                cv2.THRESH_TRUNC
                cv2.THRESH_TOZERO
                cv2.THRESH_TOZERO_INV
        """
        # type_ = 0  # cv2.THRESH_BINARY
        # if otsu:
        #     type_ += 8  # cv2.THRESH_OTSU
        type_ = 8 if otsu else 0
        ret, im2 = cv2.threshold(im_arr, thresh, maxval, type_)
    else:  # numpy
        if maxval == 255:
            im2 = ((im_arr < thresh) * 255).astype("uint8")
        else:
            im2 = np.zeros(im_arr.shape, dtype="uint8")
            im2[im_arr > maxval] = 255
            im2[im_arr < thresh] = 255

    return im2


def threshold2(im_arr, thresh, maxval=255, type_=0, otsu=False):

    if Backend == "numpy":
        im2 = ((im_arr > thresh) * 255).astype("uint8")

    elif Backend == "pillow":
        pass

    elif Backend == "opencv":
        if otsu and type_ < 8:
            type_ += 8  # cv2.THRESH_OTSU
        ret, im2 = cv2.threshold(im_arr, thresh, maxval, type_)
        return im2

    else:
        print("敬请期待")

    return im2
