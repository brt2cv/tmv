import numpy as np
import cv2
# from .image import *

def get_box_sides(box):
    # 计算高和宽
    height = round(np.linalg.norm(box[0] - box[1]), 3)
    width = round(np.linalg.norm(box[0] - box[3]), 3)
    if height < width:
        height, width = width, height
    return (width, height)

def take_picture(cnts, bkg1size, color=(255,255,255), thinckness=3):
    """ Params:
          - cnts:
            1. ndarray of cv2.contour
            2. Contour object
            3. list of thems.
          - bkg1size:
            1. image_bkg
            2. tuple_size
    """
    if isinstance(bkg1size, tuple):
        size = bkg1size
        im_bkg = np.zeros([*size, 3], np.uint8)
    else:
        im_bkg = bkg1size.copy()

    list_cnts = []
    def append_cnt(cnt_item):
        if isinstance(cnt_item, Contour):
            cnt_item = cnt_item.ndarray

        # cnt_item = np.int32(cnt_item).tolist()
        list_cnts.append(cnt_item)

    if isinstance(cnts, list):
        for cnt in cnts:
            append_cnt(cnt)
    else:  # 仅绘制一个轮廓
        append_cnt(cnts)

    # im_bkg2 = convert(im_bkg, "RGB")
    cv2.drawContours(im_bkg, list_cnts[0], -1, color, thinckness)
    return im_bkg


class Contour:
    def __init__(self, array):
        """ Params:
              - arg:
                1. ndarray of cv2.contour
                2. list tuple of (x,y)
                3. list tuple of QPointF(x,y)
                # 4. img of binary --> 用于find_contours
        """
        # self.ndarray = None
        self.load(array)

    def load(self, array):
        def _list2cnts(list_):
            """ list_: [QPointF(x,y), ...] or [(x,y), ...] """
            try:
                x, y = list_[0]
            except:
                isTuple = False
            else:
                isTuple = True

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

        if isinstance(array, np.ndarray):
            self.ndarray = array
        elif isinstance(array, list):
            self.ndarray = _list2cnts(array)
        else:
            raise Exception(f"Unknown type of array: 【{array}】")

    #####################################################################
    def get_area(self):
        area = cv2.contourArea(self.ndarray)  # 获取面积
        return area

    def get_aspect_ratio(self):
        """ 比例范围从 0.1-10 映射为整数 """
        rect = cv2.minAreaRect(self.ndarray)  # 最小外接矩形
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

    def get_length(self):
        length = cv2.arcLength(self.ndarray, False)
        return length

    def get_perimeter(self):
        length = cv2.arcLength(self.ndarray, True)  # 闭合的形状
        return length

    def _minAreaRect(self):
        # return: [[中心坐标]、[宽度, 高度]、[旋转角度]]，其中，角度是度数形式，不是弧度数
        rect = cv2.minAreaRect(self.ndarray)
        return rect  # [center, size, angle]

    def get_rect_center(self):
        center = self._minAreaRect()[0]
        return center

    def get_rect_size(self):
        size = self._minAreaRect()[1]
        return size

    def get_rect_angle(self):
        angle = self._minAreaRect()[2]
        return angle

    #####################################################################
    def approx_bbox(self):
        """ 拟合无旋转角度的矩形边框 """
        x, y, w, h = cv2.boundingRect(self.ndarray)
        return (x, y, w, h)

    def approx_rect(self, toInt=False):
        """ 最小外接矩形 """
        rect = cv2.minAreaRect(self.ndarray)
        box = cv2.boxPoints(rect)  # 获得角点坐标 [[0,0], [0,1], [1,1], [1,0]]
        if toInt:
            box = np.int32(box).tolist()
        return box

    def approx_circle(self, toInt=False):
        """ 最小外接圆 """
        center, radius = cv2.minEnclosingCircle(self)
        # (x,y) = center
        if toInt:
            center = np.int32(center).tolist()
            radius = np.int32(radius)
        return (center, radius)

    def approx_ellipse(self):
        """ 最小外接椭圆 """
        ellipse = cv2.fitEllipse(self)
        return ellipse

    def approx_polygon(self, epsilon=0):  # 多边形拟合
        """
        void approxPolyDP(InputArray curve, OutputArray approxCurve, double epsilon, bool closed)
        参数:
            - InputArray curve:        一般是由图像的轮廓点组成的点集
            - OutputArray approxCurve: 表示输出的多边形点集
            - double epsilon:          主要表示输出的精度，就是另个轮廓点之间最大距离数
            - bool closed:             表示输出的多边形是否封闭
        """
        if epsilon <= 0:
            epsilon = 0.1 * self.get_length(self)

        polygon = cv2.approxPolyDP(self, epsilon, True)
        return polygon

    def isConvex(self):  # 检测轮廓的凸性
        isConvex = cv2.isContourConvex(self)
        return isConvex

    def approx_convex(self):  # 凸包
        """
        hull = cv2.convexHull(points, hull, clockwise, returnPoints)
        参数：
            - points:       轮廓
            - hull:         输出，通常不需要
            - clockwise:    方向标志，如果设置为True，输出的凸包是顺时针方向的，否则为逆时针方向
            - returnPoints: 默认值为True，它会返回凸包上点的坐标，如果设置为False，就会返回与凸包点对应的轮廓上的点
        """
        hull = cv2.convexHull(self)
        return hull


class ContoursCollection:
    """ 组合了 list_cnts 与 bkg 的显示 """
    def __init__(self, list_cnts):
        """ Params:
              - list_cnts:
                  * list of Contour
                  * list of ndarray of cv2.contour
        """
        self.load(list_cnts)

    # def __len__(self):
    #     return len(self.list_cnts)

    def size(self):
        return len(self.list_cnts)

    def set_bkg(self, bkg1size, color=(255,0,0), thinckness=3):
        if isinstance(bkg1size, tuple):
            size = bkg1size
            im_bkg = np.zeros([*size, 3], np.uint8)
        else:
            # 如果为灰度图，转为RGB
            im_bkg = gray2bgr(bkg1size) if isGray(bkg1size) else bkg1size.copy()

        self.showing_bkg = im_bkg
        self.showing_color = color
        self.showing_thinckness = thinckness

    def get_image(self):
        im_bkg = self.showing_bkg.copy()
        cv2.drawContours(
                im_bkg,
                [ cnt.ndarray for cnt in self.list_cnts],
                -1,  # 全部
                self.showing_color,
                self.showing_thinckness)
        return im_bkg

    def load(self, list_cnts):
        if not list_cnts:
            self.list_cnts = []
            return

        if isinstance(list_cnts[0], Contour):
            self.list_cnts = list_cnts
            return

        self.list_cnts = []
        for array in list_cnts:
            cnt = Contour(array)
            self.list_cnts.append(cnt)

    def traverse(self, str_method):
        """ 回调格式: callback(cnt) --> any
            return: list of any
        """
        list_created = []
        for cnt in self.list_cnts:
            callback = eval(f"cnt.{str_method}")
            created = callback()
            if created is None:
                continue
            list_created.append(created)
        return list_created

    def get_cnts_range(self, str_method):
        """ 回调格式: cnt.str_method() --> int
            return: tuple(min, max)
        """
        list_values = self.traverse(str_method)
        min_ = min(list_values)
        max_ = max(list_values)
        return [min_, max_]

    # def get_cnts_max(self, callback):
    #     max_ = self.get_cnts_range(callback)[1]
    #     return max_

    # def get_cnts_min(self, callback):
    #     min_ = self.get_cnts_range(callback)[0]
    #     return min_

    # def sort_cnts(self, callback):
    #     """ return a list of ContourData """
    #     raise Exception("unfinished")

    def filter_cnts(self, str_method, range_pair):
        """ return a ContoursCollection of filters
            回调格式: callback(cnt) --> int
        """
        min_, max_ = range_pair
        if min_ < 0 and max_ < 0:
            return self

        results = []
        for cnt in self.list_cnts:
            callback = eval(f"cnt.{str_method}")
            value = callback()
            # if min_ <= value <= max_:
            #     results.append(cnt)
            if min_ >= 0 and value < min_:
                continue
            if max_ >= 0 and value > max_:
                continue
            results.append(cnt)

        collection = ContoursCollection(results)
        return collection


def find_contours(image, mode, method):
    """
    return: list of Contour

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

    cnts = ContoursCollection(cnts)
    return cnts
