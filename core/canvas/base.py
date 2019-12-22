from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPointF
from PyQt5.QtGui import QPainter
from utils.imgio import ndarray2pixmap

CURSOR_DEFAULT  = Qt.ArrowCursor
CURSOR_POINT    = Qt.PointingHandCursor
CURSOR_DRAW     = Qt.CrossCursor
CURSOR_MOVE     = Qt.ClosedHandCursor
CURSOR_GRAB     = Qt.OpenHandCursor

from utils.log import getLogger
logger = getLogger(1)


class ICanvas:
    """ 用于显示与涂鸦 """
    imageChanged = pyqtSignal()  # 仅在重新打开图像时发送，ImagePlus更新snapshot时无影响

    def load_container(self, container=None):
        if container is None:
            from ..img import ImageContainer
            container = ImageContainer()
        self.container = container

    def get_container(self):
        return self.container

    def get_image(self):
        return self.container.get_image()

    def set_image(self, im_arr):
        self.container.set_image(im_arr)
        # self.repaint()

    def load_image(self, path_file):
        self.container.load_image(path_file)
        self.imageChanged.emit()


class Canvas(QWidget, ICanvas):
    def __init__(self, parent, container=None):
        super().__init__(parent)
        self.load_container(container)
        self.painter = QPainter()
        self.scale = 1

    def img_size(self):
        im = self.get_image()
        h, w = im.shape[:2]
        return (w, h)

    def offset_to_center(self):
        s = self.scale
        area = self.size()
        w, h = self.img_size()
        w *= s
        h *= s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def out_of_pixmap(self, p):
        w, h = self.img_size()
        bool_ = not (0 <= p.x() <= w and 0 <= p.y() <= h)
        # logger.debug(f"当前点【{p}】是否出界: 【{bool_}】")
        return bool_

    def pos_into_pixmap(self, pos):
        """ 无差别处理出界点击位置
            return a tuple of (x,y)
        """
        pos = self.transform_pos(pos)
        w, h = self.img_size()

        x = pos.x()
        y = pos.y()

        if x < 0:
            x = 0
        elif x > w:
            x = w

        if y < 0:
            y = 0
        elif y > h:
            y = h

        return x, y

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        hint_size = self.minimumSizeHint()
        # logger.debug(f"当前Canvas尺寸： {hint_size}")
        return hint_size

    def minimumSizeHint(self):
        """ 调整当前QWidget的size """
        if self.get_image() is not None:
            w, h = self.img_size()
            return QSize(self.scale * w, self.scale * h)
        return super().minimumSizeHint()

    def paintEvent(self, event):
        curr_img = self.get_image()
        if curr_img is None:
            return super().paintEvent(event)

        p = self.painter
        p.begin(self)
        # p.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        # p.setRenderHint(QPainter.HighQualityAntialiasing)
        # p.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑
        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())
        pixmap = ndarray2pixmap(curr_img, None)
        p.drawPixmap(0, 0, pixmap)
        p.end()


from PyQt5.QtWidgets import QApplication
class DrawableCanvas(Canvas):
    """ 可绘制的图像背景板 """
    CREATING, EDITING = range(2)  # mode enums
    FREESTYLE, BOUNDING_BOX, POLYGON = range(3)
    MOUSE_PRESS, MOUSE_MOVE, MOUSE_RELEASE = range(3)

    shapeSelectChanged = pyqtSignal(bool)
    shapeMoved = pyqtSignal()
    drawingShape = pyqtSignal()
    drawingShapeDone = pyqtSignal()
    removeShape = pyqtSignal()

    def __init__(self, parent, container=None):
        super().__init__(parent, container)
        from .shape import ShapeBuilder

        self.mode = None  # 当前执行的操作，绘制或编辑
        self.shape = ShapeBuilder()  # 绘制点集的容器

        self.drawing_way = self.FREESTYLE

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        self.drawingShapeDone.connect(self.drawing_done)

    def drawing_start(self):
        self.shape.clear_points()
        self.mode = self.CREATING
        self.overrideCursor(CURSOR_DRAW)  # 切换鼠标显示
        self.update()

    def drawing_done(self):
        logger.debug("完成拟合点的选取，进行图形闭合...")
        self.mode = None
        self.shape.set_close()
        self.overrideCursor(CURSOR_DEFAULT)  # 切换鼠标显示
        self.update()

    #####################################################################

    def keyPressEvent(self, evt):
        key = evt.key()
        if key == Qt.Key_Escape:  # and self.current:
            print('ESC press')
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
        elif key == Qt.Key_Return and self.canCloseShape():
            self.finalise()
        elif key == Qt.Key_Left and self.selectedShape:
            self.moveOnePixel('Left')
        elif key == Qt.Key_Right and self.selectedShape:
            self.moveOnePixel('Right')
        elif key == Qt.Key_Up and self.selectedShape:
            self.moveOnePixel('Up')
        elif key == Qt.Key_Down and self.selectedShape:
            self.moveOnePixel('Down')

    def move_one_pixel(self, direction):
        def out_bound(step):
            points = [p1+p2 for p1, p2 in zip(self.selectedShape.points, [step]*4)]
            return True in map(self.outOfPixmap, points)

        unit = {'Left'  : QPointF(-1, 0),
                'Right' : QPointF(1, 0),
                'Up'    : QPointF(0, -1),
                'Down'  : QPointF(0, 1)
                }[direction]

        if out_bound(unit):
            logger.debug("已超出边界，无法移动")
            return

        for point in self.selectedShape:
            point += unit

        self.shapeMoved.emit()
        self.repaint()

    #####################################################################

    def currentCursor(self):
        cursor = QApplication.overrideCursor()
        if cursor:
            return cursor.shape()

    def overrideCursor(self, cursor):
        if self.currentCursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def restoreCursor(self):
        QApplication.restoreOverrideCursor()

    #####################################################################

    def transform_pos(self, qpoint):
        """ 将GUI的位置坐标转换为缩放画布的坐标位置 """
        return qpoint / self.scale - self.offset_to_center()

    def mousePressEvent(self, event):
        if self.drawing_way == self.BOUNDING_BOX:
            self.drawing_bounding_box(event, self.MOUSE_PRESS)
        elif self.drawing_way == self.POLYGON:
            self.drawing_polygon(event, self.MOUSE_PRESS)
        else:
            self.drawing_freestyle(event, self.MOUSE_PRESS)

    def mouseMoveEvent(self, event):
        if self.drawing_way == self.BOUNDING_BOX:
            self.drawing_bounding_box(event, self.MOUSE_MOVE)
        elif self.drawing_way == self.POLYGON:
            self.drawing_polygon(event, self.MOUSE_MOVE)
        else:
            self.drawing_freestyle(event, self.MOUSE_MOVE)

    def mouseReleaseEvent(self, event):
        if self.drawing_way == self.BOUNDING_BOX:
            self.drawing_bounding_box(event, self.MOUSE_RELEASE)
        elif self.drawing_way == self.POLYGON:
            self.drawing_polygon(event, self.MOUSE_RELEASE)
        else:
            self.drawing_freestyle(event, self.MOUSE_RELEASE)

    def drawing_bounding_box(self, event, mouse_status):
        if self.mode == self.CREATING:
            if event.button() == Qt.LeftButton:
                if mouse_status == self.MOUSE_PRESS:
                    pos = self.transform_pos(event.pos())
                    if self.out_of_pixmap(pos):  # 检查点选位置出界
                        return
                    # 起始点
                    assert len(self.shape) == 0, "按下鼠标时应为绘图的起始点，但当前 len(points) != 0"
                    self.shape.append_point(pos)

                elif mouse_status == self.MOUSE_RELEASE:
                    assert len(self.shape) == 1, f"释放鼠标时，应已经记录了起始点，\
    但当前 len(shape.list_points) = {len(self.shape.list_points)}"
                    first_point = self.shape.list_points[0]
                    first_x = first_point.x()
                    first_y = first_point.y()

                    x, y = self.pos_into_pixmap(event.pos())
                    self.shape.append_point(QPointF(x, first_y))
                    self.shape.append_point(QPointF(x, y))
                    self.shape.append_point(QPointF(first_x, y))

                    self.drawingShapeDone.emit()

                else:
                    pass

            elif event.button() == Qt.RightButton:
                self.drawingShapeDone.emit()

        elif self.mode == self.EDITING:
            pass

        else:
            pass

    def drawing_polygon(self, event, mouse_status):
        if mouse_status != self.MOUSE_PRESS:
            return

        if self.mode == self.CREATING:
            if event.button() == Qt.LeftButton:
                curr_pos = self.transform_pos(event.pos())
                self.shape.append_point(curr_pos)
                logger.debug(f"左键点选，已选择【{len(self.shape)}】")

            elif event.button() == Qt.RightButton:
                self.drawingShapeDone.emit()

        elif self.mode == self.EDITING:
            pass

        else:
            pass

    def drawing_freestyle(self, event, mouse_status):
        if self.mode == self.CREATING:
            if event.button() == Qt.LeftButton:
                if mouse_status == self.MOUSE_PRESS:
                    assert len(self.shape) == 0, "按下鼠标时应为绘图的起始点，但当前 len(points) != 0"
                    pos = self.transform_pos(event.pos())
                    self.shape.append_point(pos)

                if mouse_status == self.MOUSE_RELEASE:
                    logger.debug(f"当前shape集中包含【{len(self.shape)}】个点")
                    self.drawingShapeDone.emit()

            else:  # 按下鼠标左键拖动时，event.button() == 0 (Qt::NoButton)
                if mouse_status == self.MOUSE_MOVE and len(self.shape) > 0:
                    pos = self.transform_pos(event.pos())
                    self.shape.append_point(pos)
                    # self.update()  # 会调用paintEvent()

        elif self.mode == self.EDITING:
            pass

        else:
            pass

    def paintEvent(self, event):  # overwrite
        curr_img = self.get_image()
        if curr_img is None:
            return super().paintEvent(event)

        p = self.painter
        p.begin(self)
        # p.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        # p.setRenderHint(QPainter.HighQualityAntialiasing)
        # p.setRenderHint(QPainter.SmoothPixmapTransform)  # 平滑
        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())
        pixmap = ndarray2pixmap(curr_img, None)
        p.drawPixmap(0, 0, pixmap)

        # 绘制自由锚框
        self.shape.paint(p)
        p.end()
