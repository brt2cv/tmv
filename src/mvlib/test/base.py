import mvlib
import numpy as np
np.set_printoptions(threshold=np.inf)

# mvlib.set_backend("pillow")
mvlib.set_backend("skimage")
im = mvlib.imread("sample.jpg")
im_gray = mvlib.rgb2gray(im)

im_bin = mvlib.threshold(im_gray)
im_dil = mvlib.dilation(im_bin, mvlib.kernal([11, ], "square"))
im_blur = mvlib.gaussian(im_dil, 3)
im2 = mvlib.resize(im_blur, (300,600), True)

mvlib.imsave("save.jpg", im2)
