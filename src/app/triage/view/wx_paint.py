from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QPolygon

from utils.log import getLogger
logger = getLogger(1)

# 使用以下方式进行绘图：
# * painter.drawLine()
# * painter.drawPoint()
# * painter.drawRect()
# * painter.drawEllipse()
# * painter.drawPolygon()
# * painter.drawText()
# * painter.drawPie()
# * painter.drawArc()
# * painter.drawPath()


class InterfacePaint(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mouse_trace = []

    def paintEvent(self, event):
        # if not self.needUpdate:
        #     return  # 无效 ??

        painter = QPainter()
        painter.begin(self)

        color = QColor(0xFF, 0, 0)  # Qt.black
        # color.setNamedColor('#d4d4d4')
        line_width = 2
        line_style = Qt.SolidLine
        painter.setPen(QPen(color, line_width, line_style))

        # self.paint_freestyle(painter)
        self.paint_polygon(painter)

        painter.end()
        # self.update()  # 如果在paintEvent()中调用update(),cpu占用很高！

    def paint_freestyle(self, painter):
        # logger.debug(f">> the length of list_trace: {len(self.mouse_trace)}")
        if len(self.mouse_trace) > 1:
            pos_last = self.mouse_trace[0]
            for pos in self.mouse_trace[1:]:
                painter.drawLine(pos_last.x(), pos_last.y(), pos.x(), pos.y())
                pos_last = pos

    def paint_polygon(self, painter):
        if len(self.mouse_trace) == 2:
            pos0, pos1 = self.mouse_trace
            painter.drawLine(pos0.x(), pos0.y(), pos1.x(), pos1.y())
        elif len(self.mouse_trace) > 2:
            painter.setBrush(Qt.blue)  # 填充色
            polygon = QPolygon(self.mouse_trace)
            # polygon.setPoints(self.mouse_trace)
            painter.drawPolygon(polygon)

    def mouseMoveEvent(self, event):
        self.mouse_trace.append(event.pos())
        self.update()  # 会调用paintEvent()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            logger.debug("清空当前线条")
            self.mouse_trace.clear()
        else:
            self.mouse_trace.append(event.pos())
        self.update()
