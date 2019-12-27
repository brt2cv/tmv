from .backend import get_backend

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
