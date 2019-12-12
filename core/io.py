from util import imgio
from .img import ImagePlus

def imread(path_file):
    im = imgio.imread(path_file)
    ips = ImagePlus(im)
    return ips

def imwrite(path_save, ips):
    imgio.imwrite(path_save, ips)

imsave = imwrite
