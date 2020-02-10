from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    from skimage import transform
if include("scipy"):
    from scipy import ndimage
if include("numpy"):
    import numpy as np
if include("pillow"):
    from PIL import Image


def resize(im, output_shape, antialias=True):
    """ output_shape: (h, w) """
    def run_skimage():
        # 默认
        im_float64 = transform.resize(im, output_shape, order=0, anti_aliasing=antialias)
        return (im_float64 * 255).astype("uint8")

    def run_opencv():
        """
        interpolation:
            INTER_NEAREST   - 最近邻插值法
            INTER_LINEAR    - 双线性插值法（默认）
            INTER_AREA      - 基于局部像素的重采样（resampling using pixel area relation）。对于图像抽取（image decimation）来说，这可能是一个更好的方法。但如果是放大图像时，它和最近邻法的效果类似;
            INTER_CUBIC     - 基于4x4像素邻域的3次插值法
            INTER_LANCZOS4  - 基于8x8像素邻域的Lanczos插值
        """
        # 注意：pillow.size 与 ndarray.size 顺序不同
        h, w = output_shape
        return cv2.resize(im, dsize=(w, h))

    def run_pillow():
        # 开启抗锯齿，耗时增加8倍左右
        resample = Image.ANTIALIAS if antialias else Image.NEAREST
        # pillow.size自成体系，无需多余处理（错上加错就OK了）
        return im.resize(output_shape, resample)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv,
            func_pillow=run_pillow
        )()

def rescale(im, scale):
    """ scale could be float or tuple like [0.2, 0.3] """
    def run_skimage():
        return transform.rescale(im, scale)

    def run_opencv():
        try:
            fx, fy = scale
        except TypeError:
            fx = fy = scale
        return cv2.resize(im, None, fx, fy)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv
        )()

def rotate(im, angle):
    def run_skimage():
        return transform.rotate(im, angle)

    def run_opencv():
        # cv2.flip(im, flipCode)  # 翻转
        cols, rows = im.shape[:2]
        # cols-1 and rows-1 are the coordinate limits.
        M = cv2.getRotationMatrix2D(((rows-1)/2, (cols-1)/2), angle, 1)
        return cv2.warpAffine(im, M, (rows, cols))

    def run_pillow():
        # expand：如果设为True，会放大图像的尺寸，以适应旋转后的新图像
        return im.rotate(angle, expand=False)

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv,
            func_pillow=run_pillow
        )()

def pyramid(im, downscale, method="gaussian"):
    def run_skimage():
        map_func = {
            "gaussian": transform.pyramid_gaussian,
            "laplacian": transform.pyramid_laplacian
        }
        return map_func[method](im, downscale)

    return run_backend(
            func_skimage=run_skimage,
        )()
