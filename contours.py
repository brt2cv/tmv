from .backend import run_backend, include

if include("opencv"):
    import cv2
if include("skimage"):
    from skimage import feature
if include("numpy"):
    import numpy as np
# if include("scipy"):
#     from scipy import ndimage
# if include("pillow"):
#     from PIL import Image


def list2cnts(list_):
    """ list_: [QPointF(x,y), ...] or [(x,y), ...] """
    isTuple = True
    try:
        x, y = list_[0]
    except:
        isTuple = False

    list_cnts = []  # 维度为3 --> (n,1,2)
    for point in list_:
        if isTuple:
            x, y = point
        else:
            x = point.x()
            y = point.y()

        point = [[x, y]]  # 这个结构很特殊，多一层[]
        list_cnts.append(point)

    cnts = np.asarray(list_cnts, dtype="float32")  # 必须为np.float32
    return cnts


def find_cnts(image, mode=0, method=1):
    def run_opencv():
        """
        return: list of ndarray(dtype=int32)
            - one contours is like this: [[[234, 123]], [[345, 789]], ...]

        mode, 轮廓的检索模式:
            - cv2.RETR_EXTERNAL 表示只检测外轮廓
            - cv2.RETR_LIST 检测的轮廓不建立等级关系
            - cv2.RETR_CCOMP 建立两个等级的轮廓，上面的一层为外边界，里面的一层为内孔的边界信息。如果内孔内还有一个连通物体，这个物体的边界也在顶层。
            - cv2.RETR_TREE 建立一个等级树结构的轮廓。

        method, 轮廓的近似办法:
            - cv2.CHAIN_APPROX_NONE 存储所有的轮廓点，相邻的两个点的像素位置差不超过1，即max（abs（x1-x2），abs（y2-y1））==1
            - cv2.CHAIN_APPROX_SIMPLE 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需4个点来保存轮廓信息
            - cv2.CHAIN_APPROX_TC89_L1，CV_CHAIN_APPROX_TC89_KCOS使用teh-Chinl chain 近似算法
        """
        list_ret = cv2.findContours(image, mode, method)
        try:
            # hierarchy: 各层轮廓的索引
            cnts, hierarchy = list_ret
        except ValueError:
            _, cnts, hierarchy = list_ret
        return cnts

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()


def cnts2img(contours, im_bkg, line_color, thinckness=3):
    def run_opencv():
        cv2.drawContours(im_bkg, contours, -1, line_color, thinckness)
        return im_bkg

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

##############################################################################

def approx_bounding(cnt):
    """ 拟合矩形边框 """
    def run_opencv():
        x, y, w, h = cv2.boundingRect(cnt)
        return (x, y, w, h)

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def approx_rect(cnt):
    """ 最小外接矩形 """
    def run_opencv():
        rect = cv2.minAreaRect(cnt)  # return: [[中心坐标]、[宽度, 高度]、[旋转角度]]，其中，角度是度数形式，不是弧度数
        box = cv2.boxPoints(rect)  # 获得角点坐标
        box = np.int0(box)  # np.uint8(box)... 额，uint8错误！
        return box  # [[0,0], [0,1], [1,1], [1,0]]

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def approx_circle(cnt):
    """ 最小外接圆 """
    def run_opencv():
        center, radius = cv2.minEnclosingCircle(cnt)  # (x,y) = center
        center = tuple(np.int0(center))  # 转换为整型
        radius = np.int0(radius)
        return (center, radius)

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def approx_ellipse(cnt):
    """ 最小外接椭圆 """
    def run_opencv():
        ellipse = cv2.fitEllipse(cnt)
        return ellipse

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def approx_polygon(cnt, epsilon=0):  # 多边形拟合
    """
    void approxPolyDP(InputArray curve, OutputArray approxCurve, double epsilon, bool closed)
    参数:
        - InputArray curve:        一般是由图像的轮廓点组成的点集
        - OutputArray approxCurve: 表示输出的多边形点集
        - double epsilon:          主要表示输出的精度，就是另个轮廓点之间最大距离数
        - bool closed:             表示输出的多边形是否封闭
    """
    def run_opencv():
        if epsilon <= 0:
            epsilon = 0.1 * cnt_length(cnt)

        polygon = cv2.approxPolyDP(cnt, epsilon, True)
        return polygon

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def isConvex(cnt):  # 检测轮廓的凸性
    def run_opencv():
        isConvex = cv2.isContourConvex(cnt)
        return isConvex

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()


def approx_convex(cnt):  # 凸包
    def run_opencv():
        """
        hull = cv2.convexHull(points, hull, clockwise, returnPoints)
        参数：
            - points:       轮廓
            - hull:         输出，通常不需要
            - clockwise:    方向标志，如果设置为True，输出的凸包是顺时针方向的，否则为逆时针方向
            - returnPoints: 默认值为True，它会返回凸包上点的坐标，如果设置为False，就会返回与凸包点对应的轮廓上的点
        """
        hull = cv2.convexHull(cnt)
        return hull

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

##############################################################################

def cnt_area(cnt):
    def run_opencv():
        area = cv2.contourArea(cnt)  # 获取面积
        return area

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def cnt_aspect_ratio(cnt):
    """ 比例范围从 0.1-10 映射为整数 """
    def run_opencv():
        rect = cv2.minAreaRect(cnt)  # 最小外接矩形
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])
        if height == 0:
            return
        ratio = width / height
        # 映射为整数
        ratio = int(100*ratio)
        return ratio

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def cnt_length(cnt):
    def run_opencv():
        length = cv2.arcLength(cnt, True)  # 闭合的形状
        return length

    return run_backend(
            # func_skimage=run_skimage,
            func_opencv=run_opencv,
            # func_pillow=run_pillow,
            # func_numpy=run_numpy,
        )()

def get_box_sides(box):
    # 计算高和宽
    height = round(np.linalg.norm(box[0] - box[1]), 3)
    width = round(np.linalg.norm(box[0] - box[3]), 3)
    if height < width:
        height, width = width, height
    return (width, height)


class ContoursCollection:
    def __init__(self, list_cnts):
        self.cnts = list_cnts

    def __len__(self):
        return self.size()

    def size(self):
        return len(self.cnts)

    def show(self, bkg1size, color=(255,255,255), thinckness=3):
        img = cnts2img(self.cnts, bkg1size, color, thinckness)
        return img

    def traverse(self, callback):
        """ 回调格式: callback(cnt) --> any
            return: list of any
        """
        list_created = []
        for cnt in self.cnts:
            created = callback(cnt)
            if created is None:
                continue
            list_created.append(created)
        return list_created

    def get_cnts_range(self, callback):
        """ 回调格式: callback(cnt) --> int
            return: tuple(min, max)
        """
        list_values = self.traverse(callback)
        min_ = min(list_values)
        max_ = max(list_values)
        return (min_, max_)

    # def get_cnts_max(self, callback):
    #     max_ = self.get_cnts_range(callback)[1]
    #     return max_

    # def get_cnts_min(self, callback):
    #     min_ = self.get_cnts_range(callback)[0]
    #     return min_

    # def sort_cnts(self, callback):
    #     """ return a list of ContourData """
    #     raise Exception("unfinished")

    def filter_cnts(self, callback, range_pair):
        """ return a ContoursCollection of filters
            回调格式: callback(cnt) --> int
        """
        min_, max_ = range_pair
        if min_ < 0 and max_ < 0:
            return self

        results = []
        for cnt in self.cnts:
            value = callback(cnt)
            # if min_ <= value <= max_:
            #     results.append(cnt)
            if min_ >= 0 and value < min_:
                continue
            if max_ >= 0 and value > max_:
                continue
            results.append(cnt)

        collection = ContoursCollection(results)
        return collection


if __name__ == "__main__":
    cnts = ContoursCollection([])
    print(len(cnts))
