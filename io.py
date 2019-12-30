from .backend import run_backend, include, get_backend

if include("opencv"):
    import cv2
if include("skimage"):
    import skimage
# if include("scipy"):
#     from scipy import ndimage
if include("numpy"):
    import numpy as np

#####################################################################

if get_backend() == "pillow":
    from PIL import Image

    def imread(path_file):
        """ return a PIL::Image object """
        return Image.open(path_file)

    def imwrite(path_file, im):
        im.save(path_file)

    imsave = imwrite

else:
    from imageio import imread, imwrite, imsave


def float2ubyte(im):
    def run_numpy():
        return (im * 255).astype(np.uint8)

    def run_skimage():
        return skimage.img_as_ubyte(im)

    return run_backend(
            func_numpy=run_numpy,
            func_skimage=run_skimage
        )()
