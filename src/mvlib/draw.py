# https://zhuanlan.zhihu.com/p/59849190 --> PIL.ImageDraw
# https://blog.csdn.net/vcx08/article/details/79010892 --> OpenCV.Drawing
# https://blog.csdn.net/sinat_34707539/article/details/51912610  # cv2的原型说明
# https://scikit-image.org/docs/stable/api/skimage.draw.html --> skimage

from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    import skimage
if include("numpy"):
    import numpy as np
# if include("scipy"):
#     from scipy import ndimage
if include("pillow"):
    from PIL.ImageColor import getrgb  # colormap
    from PIL import Image, ImageDraw
    from .img import get_mode
    from utils.imgio import pillow2ndarray


from utils.log import getLogger
logger = getLogger()


def pil_drawing(im_arr, func_name, data, color, **kwargs):
    """ 此处的color表示outline_color """
    if func_name in ["arc", "line", "point", "text"]:
        kwargs["fill"] = color
    else:
        kwargs["outline"] = color

    mode = get_mode(im_arr)
    img_pil = Image.fromarray(im_arr, mode)
    # 转换为彩图显示
    gray_colors = [None, "white", "black"]
    isDrawRGB = kwargs.get("fill") not in gray_colors or \
                kwargs.get("outline") not in gray_colors
    if mode == "L" and isDrawRGB:
        img_pil = img_pil.convert("RGB")

    draw = ImageDraw.Draw(img_pil)  # 提供eval使用
    name2func = {
        "arc"   : draw.arc,         # draw.arc((100, 200, 300, 400), 0, 180, 'yellow')
                                    # draw.arc((100, 200, 300, 400), -90, 0, 'green')
        "chord" : draw.chord,       # draw.chord((350, 50, 500, 200), 0, 120, 'khaki', 'orange')
        "line"  : draw.line,        # draw.line((20, 20, 150, 150), 'cyan')
        "point" : draw.point,
        "text"  : draw.text,        # font = ImageFont.truetype("consola.ttf", 40, encoding="unic")
                                    # draw.text((100, 50), u'Hello World', 'fuchsia', font)
        "rect"  : draw.rectangle,   # draw.rectangle((100, 200, 300, 400), 'black', 'red')
        "pie"   : draw.pieslice,    # draw.pieslice((350, 50, 500, 200), -150, -30, 'pink', 'crimson')
        "polygon"   : draw.polygon, # draw.polygon((150, 180, 200, 180, 250, 120, 230, 90, 130, 100), 'olive', 'hotpink')
        "ellipse"   : draw.ellipse, # draw.ellipse((350, 300, 500, 400), 'yellowgreen', 'wheat')
        "circle"    : draw.ellipse, # draw.ellipse((550, 50, 600, 100), 'seagreen', 'skyblue')
    }
    # callback = eval("draw." + func_name)
    name2func[func_name](data, **kwargs)
    im_output = pillow2ndarray(img_pil)
    return im_output

def point(im_arr, list_pnts, color, width=1):
    """ draw a point """

def line(im_arr, list_pnts, color, width=1):
    def run_pillow():
        return pil_drawing(im_arr, "line", list_pnts, color,
                           width=width)
    def run_skimage():
        im2 = im_arr.copy()

        first = list_pnts[0]
        for second in list_pnts[1:]:
            rr, cc = draw(*first, *second)
            tuple_color = getrgb(color)
            draw.set_color(im2, [rr, cc], tuple_color)
            first = second
        return im2

    def run_opencv():
        return cv2.line()

    return run_backend(
            func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_numpy=run_numpy,
            func_pillow=run_pillow
        )()

def polygon(im_arr, list_pnts, color, width=1):
    def run_pillow():
        if width > 1:  # and "fill" not in kwargs:
            # 将不支持填充
            logger.warning("PIL绘图模块不支持polygon线宽设置，使用封闭直线段的方式绘图")
            if isinstance(list_pnts, np.ndarray):
                pnts_closed = np.append(list_pnts, [list_pnts[0]], axis=0)
            else:
                pnts_closed = list_pnts + list_pnts[0]
            logger.debug(f"封闭直线段 >> {pnts_closed}")
            im2 = line(im_arr, pnts_closed, color, width)
        else:
            if width > 1:
                logger.warning("PIL绘图模块不支持polygon线宽设置")
            im2 = pil_drawing(im_arr, "polygon", list_pnts, color)  # 不支持width!
        return im2

    return run_backend(
            # func_skimage=run_skimage,
            # func_opencv=run_opencv,
            # func_numpy=run_numpy,
            func_pillow=run_pillow
        )()

def rectangle(im_arr, list_pnts, color, width=1):
    im2 = im_arr.copy()

    def run_pillow():
        return pil_drawing(im_arr, "rect", list_pnts, color,
                          width=width)

    return run_backend(
            # func_skimage=run_skimage,
            # func_opencv=run_opencv,
            # func_numpy=run_numpy,
            func_pillow=run_pillow
        )()

# rect = polygon
rect = rectangle

#####################################################################

if False:
    import numpy as np
    import cv2

    from .image import isColored

    # keypoints = detector.detect(im)
    def draw_keypoints(img, keypoints, color=(0,255,0)):
        im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), color,
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return im_with_keypoints

    # https://blog.csdn.net/vcx08/article/details/79010892
    # https://blog.csdn.net/sinat_34707539/article/details/51912610  # cv2的原型说明
    draw_line = cv2.line

    draw_circle = cv2.circle
    """ cv2.circle(img, (x,y), radius, (0, 255, 0), 2) """

    draw_ellipse = cv2.ellipse
    """ cv2.ellipse(img, center, axes, angle, startAngle, endAngle, color[, thickness[, lineType[, shift]]]) → img

        example:
            cv2.ellipse(img, ellipse_left, (0,255,0), 1)
            cv2.ellipse(img,(x,y),(100,50),0,0,180,(20,213,79), 2)

        params:
            img:         图片
            center:      椭圆中心(x,y)
            axes:        x/y轴的长度
            angle:       angle--椭圆的旋转角度
            startAngle:  startAngle--椭圆的起始角度
            endAngle:    endAngle--椭圆的结束角度
            color:       颜色
    """

    draw_contours = cv2.drawContours

    draw_polygon = cv2.polylines
    """ cv2.polylines(image, [approx], True, (0, 255, 0), 2) """

    draw_rect = cv2.rectangle
    """ cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2) """

    draw_text = cv2.putText
    """ cv2.putText(img, str(info), (left, top)), font, 0.5, (0,0,255), 1) """

    # def draw_rect(img, left_top, right_bottom, *args, **kwargs):
    #     """ args: color, thickness, line_type """
    #     im_copy = img.copy()
    #     cv2.rectangle(im_copy, left_top, right_bottom, *args, **kwargs)
    #     return im_copy

    # def draw_text(img, text, origin, *args, **kwargs):
    #     """ args: font, size, color, thickness """
    #     im_copy = img.copy()
    #     # 使用推荐字体 linetype=cv2.LINE_AA（16）
    #     cv2.putText(im_copy, text, origin, line_type=cv2.LINE_AA, *args, **kwargs)
    #     return im_copy

    # def make_roi(img, left_top, width, height):
    #     """ return a copy of ROI """
    #     left, top = left_top
    #     roi = img[top:(top + height), left:(left + width)]
    #     return roi

    def draw_roi(img, left_top, width, height):
        line_width = 2
        line_color = (0, 0, 255) if isColored(img) else 255
        im_ = img.copy()
        left, top = left_top

        left_ = left -line_width
        top_ = top -line_width
        cv2.rectangle(im_, (left_, top_), (left + width + line_width -1, top + height + line_width -1),
                      line_color, line_width)
        # dev_imshow(im, "ROI区域位置")
        return im_
