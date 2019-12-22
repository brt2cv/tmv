from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QIcon

from utils.qt5 import dialog_file_select

from mvlib.contours import *
from mvlib import draw
from mvlib.morphology import *
from mvlib.color import rgb2gray
from mvlib.filters import threshold

from core.img import ImagePlus

from utils.log import getLogger
logger = getLogger(1)

import os.path
dir_res = os.path.join(os.path.dirname(__file__), "../res")

class MainWnd(QWidget):
    def __init__(self, parent, attach=None):
        from utils.uic import loadUi

        super().__init__(attach if attach is not None else parent)
        loadUi("ui/wx_viewer.ui", self)
        self.setProperty("class", "bkg")  # for qss
        self._setup_ui()

        self.setWindowTitle("伤口测量工具")
        self.setWindowIcon(QIcon(f"{dir_res}/measure.png"))
        self.resize(600, 450)
        # self.move(0, 0)
        # self.canvas.load_image("tmp/art.jpg")

    def _setup_ui(self):
        from PyQt5.QtWidgets import QStatusBar, QSizePolicy
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("打开图像，点击绘制轮廓进行尺寸分析")
        self.ly_footer.addWidget(self.status_bar)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.status_bar.setSizePolicy(sizePolicy)

        # Ctrl-Zone:
        # self._setup_ctrl_zone()

        from core.ui.scroll_canvas import ImageScrollCanvasWithPainter
        # from core.ui.scroll_canvas import ImageScrollCanvas

        self.canvas = ImageScrollCanvasWithPainter(self)
        self.ly_show.addWidget(self.canvas)

        #####################################################################
        from PyQt5.QtWidgets import QToolBar, QAction

        toolbar = QToolBar("Default", self)
        open_img = QAction(QIcon(f"{dir_res}/open.png"), "打开图像", self)
        toolbar.addAction(open_img)
        open_img.triggered.connect(self.on_open_image)

        def canvas_reset():
            self.ppi = None
        self.canvas.imageChanged.connect(canvas_reset)

        save_data = QAction(QIcon(f"{dir_res}/save.png"), "保存到数据库", self)
        toolbar.addAction(save_data)
        open_img.triggered.connect(self.save_data)

        scale = QAction(QIcon(f"{dir_res}/scale.png"), "尺寸标定", self)
        toolbar.addAction(scale)
        scale.triggered.connect(self.ruler_calibration)

        draw_cnt = QAction(QIcon(f"{dir_res}/color_line.png"), "手动绘制轮廓", self)
        toolbar.addAction(draw_cnt)
        draw_cnt.triggered.connect(self.canvas.drawing_start)

        find_cnt = QAction(QIcon(f"{dir_res}/objects.png"), "自动查找伤口区域", self)
        toolbar.addAction(find_cnt)
        find_cnt.triggered.connect(self.on_find_cnts)

        measure_cnt = QAction(QIcon(f"{dir_res}/measure.png"), "测量尺寸", self)
        toolbar.addAction(measure_cnt)
        measure_cnt.triggered.connect(self.on_calculate_contours)

        self.ly_header.addWidget(toolbar)

        self._setup_ctrl()

    def _setup_ctrl(self):
        from utils.qt5wx.wx_unit import UnitSlider
        slider = UnitSlider(self, "阈值", val_range=[0, 255], isCheckbox=False)
        self.ly_ctrl.addWidget(slider)

        def threshold_(value):
            ips = self.canvas.get_image()
            im_raw = ips.get_snap()
            gray = rgb2gray(im_raw)
            thresh = threshold(gray, value)
            ips_thresh = ImagePlus(thresh, ips.meta)
            self.canvas.set_image(ips_thresh)

        slider.set_slot(threshold_)

    def on_open_image(self):
        file_path = dialog_file_select(self, "Images (*.png *.bmp *.jpg)")
        if not file_path:
            return
        elif len(file_path) > 1:
            QMessageBox.warning(self, self.tr("错误"), self.tr("请勿选择多张图片"))
            return

        path_pic = file_path[0]
        # try:
        #     from core.io import imread
        #     img = imread(path_pic)
        # except Exception as e:
        #     logger.error(f"载入图像失败：{e}")
        #     QMessageBox.warning(self, self.tr("错误"), self.tr("无法载入图像，路径是否含有中文？"))
        #     return
        self.canvas.load_image(path_pic)

    def ruler_calibration(self):
        list_points = self.canvas.canvas.shape.list_points
        if not list_points:
            return
        cnt = Contour(list_points)

        # get the scale 标尺 bounding-box
        im = self.canvas.get_image()
        x, y, w, h = cnt.approx_bbox()
        # logger.debug(f"bbox: {[x, y, (x+w), (y+h)]}")

        cropped = im[y:y+h, x:x+w]
        gray = rgb2gray(cropped)
        thresh = threshold(gray, 0, 255, 1, otsu=True)

        selem = kernel((5, 5), "rect")
        im_dilation = dilation(thresh, selem, iterations=1)

        cnts = find_contours(im_dilation, 0, 1)
        if len(cnts.list_cnts) > 1:
            cnts = cnts.filter_cnts("get_area", (1000, -1))

            num_cnts = len(cnts.list_cnts)
            if num_cnts != 1:
                QMessageBox.warning(self, "警告", f"未能获得标尺的轮廓：{num_cnts}")
                return

        cnt_scale = cnts.list_cnts[0]
        width, height = cnt_scale.get_rect_size()
        ruler_length = max(width, height)
        self.ppi = ruler_length / 63  # 单位: mm
        self.status_bar.showMessage(f"标尺的长度 {ruler_length}, ppi={self.ppi}")

    def on_calculate_contours(self):
        if self.ppi is None:
            QMessageBox.warning(self, "警告", "请先执行尺寸标定")
            return

        list_points = self.canvas.canvas.shape.list_points
        if not list_points:
            return
        cnt = Contour(list_points)

        # draw the rect
        im = self.canvas.get_image()
        box = cnt.approx_rect()
        im2 = draw.polygon(im, box, "red", width=1)

        self.canvas.set_image(im2)

        # 计算尺寸
        width, height = cnt.get_rect_size()
        if width < height:
            width, height = height, width
        width = round(width / self.ppi, 3)
        height = round(height / self.ppi, 3)
        self.status_bar.showMessage(f"区域的长 {width}, 宽 {height}")

        info = f"""轮廓区域尺寸：长 {width} mm, 宽 {height} mm
轮廓区域面积：{round(cnt.get_area() / (self.ppi ** 2), 3)} mm^2
轮廓区域周长：{round(cnt.get_perimeter() / self.ppi, 3)} mm

是否保存至数据库？
"""
        reply = QMessageBox.question(self, "计算", info,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_data()
        else:
            self.canvas.canvas.shape.clear_points()
            self.canvas.set_image(im)

    def save_data(self):
        self.status_bar.showMessage("已储存数据")

    def on_find_cnts(self):
        QMessageBox.warning(self, "伤口区域自动识别", "敬请期待")
