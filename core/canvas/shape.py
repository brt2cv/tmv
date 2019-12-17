from PyQt5.QtGui import QPen, QColor, QPainterPath

from util.log import getLogger
logger = getLogger(1)

class ShapeBuilder:
    P_SQUARE, P_ROUND = range(2)  # 顶点形状
    MOVE_VERTEX, NEAR_VERTEX = range(2)

    line_color = QColor(0, 255, 0, 128)
    fill_color = QColor(255, 0, 0, 128)
    select_line_color = QColor(255, 255, 255)
    select_fill_color = QColor(0, 128, 255, 155)
    vertex_fill_color = QColor(0, 255, 0, 255)
    hvertex_fill_color = QColor(255, 0, 0)

    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self):
        self.list_points = []

        self.fill = False
        self.selected = False

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self.closed = False

    def __len__(self):
        return len(self.list_points)

    def __getitem__(self, key):
        return self.list_points[key]

    def __setitem__(self, key, value):
        self.list_points[key] = value

    def append_point(self, point):
        self.list_points.append(point)

    def clear_points(self):
        """ 清理记录点集 """
        self.list_points.clear()

    def set_close(self):
        """ 边框的闭合状态 """
        self.closed = True

    def paint(self, painter):
        """ 绘制时创建了两种元素：顶点QPainterPath和边线QPainterPath """
        if self.list_points:
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.list_points[0])

            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            # self.add_vertex(vrtx_path, 0)

            for i, p in enumerate(self.list_points):
                line_path.lineTo(p)
                self.draw_vertex(vrtx_path, i)
                # logger.debug(">> 绘制边线")
            if self.closed:
                line_path.lineTo(self.list_points[0])
                # logger.debug(">> 闭合区域")

            painter.drawPath(line_path)
            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                painter.fillPath(line_path, color)

            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)
            # logger.debug(">> 绘制顶点")

    # def draw_text(self, painter, text):
    #     # Draw text at the top-left
    #     if self.paintLabel:
    #         min_x = sys.maxsize
    #         min_y = sys.maxsize
    #         for point in self.list_points:
    #             min_x = min(min_x, point.x())
    #             min_y = min(min_y, point.y())
    #         if min_x != sys.maxsize and min_y != sys.maxsize:
    #             font = QFont()
    #             font.setPointSize(8)
    #             font.setBold(True)
    #             painter.setFont(font)
    #             if(self.label == None):
    #                 self.label = ""
    #             if(min_y < MIN_Y_LABEL):
    #                 min_y += MIN_Y_LABEL
    #             painter.drawText(min_x, min_y, self.label)

    def draw_vertex(self, painter_path, i):
        """ 为一个QPainterPath对象添加顶点 """
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.list_points[i]

        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size

        if self._highlightIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = ShapeBuilder.vertex_fill_color

        if shape == self.P_SQUARE:
            painter_path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            painter_path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    # def nearest_vertex(self, point, epsilon):
    #     for i, p in enumerate(self.list_points):
    #         if distance(p - point) <= epsilon:
    #             return i  # ??

    #####################################################################

    def highlightVertex(self, i, action):
        self._highlightIndex = i
        self._highlightMode = action

    def highlightClear(self):
        self._highlightIndex = None

    def moveBy(self, offset):
        self.list_points = [p + offset for p in self.list_points]

    def moveVertexBy(self, i, offset):
        self.list_points[i] = self.list_points[i] + offset
