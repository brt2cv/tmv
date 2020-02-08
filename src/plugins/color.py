# from PyQt5.QtWidgets import QMessageBox
from core.plugin.filter import Filter, DialogFilter
from core import g

import mvlib.color
import mvlib.filters


class Gray(Filter):
    title = 'Gray'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2gray({im})"

    def processing(self, im_arr):
        gray = mvlib.color.rgb2gray(im_arr)
        return gray


class Threshold(DialogFilter):
    title = "Threshold"
    formats = {"mode": "gray"}
    view = [{
        "type": "slider",
        "name": "阈值",
        "val_init": 128,
        "val_range": [0, 255],
        "para": "thresh"
    },{
        "type": "slider",
        "name": "阈值2",
        "val_init": 255,
        "val_range": [0, 255],
        "para": "maxval"
    }]
    # para = {"thresh": 128, "maxval": 255}
    scripts = "{output} = mvlib.filters.threshold({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        return mvlib.filters.threshold(im_arr,
                                       self.paras["thresh"],
                                       self.paras["maxval"])

class ThresholdPlus(Threshold):
    """ 高亮极值(0, 255)区域 """
    formats = {"mode": "gray", "backend": {"opencv", "skimage"}}
    view = [{
        "type": "slider",
        "name": "阈值",
        "val_init": 0,
        "val_range": [0, 255],
        "para": "thresh"
    },{
        "type": "slider",
        "name": "阈值2",
        "val_init": 255,
        "val_range": [0, 255],
        "para": "maxval"
    }]

    def processing(self, im_arr):
        thresh = self.paras["thresh"]
        maxval = self.paras["maxval"]

        im_rgb = mvlib.color.gray2rgb(im_arr)
        im_rgb[im_arr < thresh] = (0, 0, 255)
        im_rgb[im_arr > maxval] = (255, 0, 0)
        return im_rgb


class GrayStairs(DialogFilter):
    """ 灰度等级（色阶） """
    title = "Gray Stairs"
    # formats = {"mode": "gray"}  # 支持彩图
    view = [{
        "type": "slider",
        "name": "阈值",
        "val_init": 0,
        "val_range": [0, 255],
        "para": "thresh"
    },{
        "type": "slider",
        "name": "阈值2",
        "val_init": 255,
        "val_range": [0, 255],
        "para": "maxval"
    }]
    scripts = "{output} = mvlib.filters.graystairs({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        return mvlib.filters.graystairs(im_arr,
                                        self.paras["thresh"],
                                        self.paras["maxval"])


class Bright_Contrast(DialogFilter):
    title = "Bright and Contrast"
    # formats = {"mode": "gray"}  # 支持彩图
    view = [{
        "type": "slider",
        "name": "亮度 ",
        "val_init": 0,
        "val_range": [-100, 100],
        "para": "bright"
    },{
        "type": "slider",
        "name": "对比度",
        "val_init": 45,
        "val_range": [1, 89],
        "para": "contrast"
    }]
    scripts = "{output} = mvlib.filters.contrast({im}, {bright}, {contrast})"

    def processing(self, im_arr):
        return mvlib.filters.contrast(im_arr,
                                      self.paras["bright"],
                                      self.paras["contrast"])


class HistogramTool(DialogFilter):
    title = "直方图工具"  # 以及直方图标准化操作
    # formats = {"mode": "gray"}  # 支持彩图，但彩图没有任何意义
    view = [{
        "type": "pyplot",
        "name": "Histogram"
    }]
    scripts = "{output} = mvlib.filters.hist_normalize({im})"

    def setup_ui(self):
        super().setup_ui()
        self.resize(400,300)

    def processing(self, im_arr):
        return mvlib.filters.hist_normalize(im_arr)

    def preview(self):
        super().preview()

        def plot_overlay(figure):
            im_curr = self.get_curr_image()
            # 不清理之前的axes，叠加绘制
            axes = figure.get_axes()[0]
            axes.hist(im_curr.ravel(), 255)

        unit_plot = self.widgets["Histogram"]
        unit_plot.show(plot_overlay)

    def reset(self):
        super().reset()
        unit_plot = self.widgets["Histogram"]
        unit_plot.show(self.update_plot)

    def update_plot(self, figure):
        list_axes = figure.get_axes()
        axes = list_axes[0] if list_axes else figure.add_subplot(111)
        axes.clear()

        # import mvlib
        # hist, bins = mvlib.exposure.histogram()
        axes.hist(self.get_image().ravel(), 255)

    def run(self):
        if self.check_format():
            if self.needSetupUi:
                self.setup_ui()  # 延迟构造窗口UI
                self.needSetupUi = False

            # 更新pyplot显示
            unit_plot = self.widgets["Histogram"]
            unit_plot.show(self.update_plot)

            self.show()
            # 无需自动预览


class HSV_Filter(DialogFilter):
    """ HSV色值过滤 """
    title = "HSV色值过滤器"
    buttons = ["Preview", "OK"]
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.hsv_range({im}, {color_range})"
    view = [{
        "type": "slider",
        "name": "H-low ",
        "val_init": 0,
        "val_range": [0, 180],
        "para": "h_0"
    },{
        "type": "slider",
        "name": "H-high",
        "val_init": 180,
        "val_range": [0, 180],
        "para": "h_1"
    },{
        "type": "slider",
        "name": "S-low ",
        "val_init": 0,
        "val_range": [0, 255],
        "para": "s_0"
    },{
        "type": "slider",
        "name": "S-high",
        "val_init": 255,
        "val_range": [0, 255],
        "para": "s_1"
    },{
        "type": "slider",
        "name": "V-low ",
        "val_init": 0,
        "val_range": [0, 255],
        "para": "v_0"
    },{
        "type": "slider",
        "name": "V-high",
        "val_init": 255,
        "val_range": [0, 255],
        "para": "v_1"
    }]

    def processing(self, im_arr):
        self.paras["color_range"] = [
            self.paras["h_0"],
            self.paras["h_1"],
            self.paras["s_0"],
            self.paras["s_1"],
            self.paras["v_0"],
            self.paras["v_1"]
        ]
        return mvlib.color.hsv_range(im_arr, self.paras["color_range"])


class ArithmeticThreshold(DialogFilter):
    """ 比例阈值 """
    title = "比例阈值"
    buttons = ["OK", "Cancel"]
    formats = {"mode": "gray"}
    view = [{
        "type": "spinbox",
        "name": "num_row",
        "val_init": 3,
        "val_range": [1, 5],
        "para": "nRow"
    },{
        "type": "spinbox",
        "name": "num_col",
        "val_init": 3,
        "val_range": [1, 5],
        "para": "nColumn"
    }]

    def processing(self, im_arr):
        num_total = self.paras["nRow"] * self.paras["nColumn"]
        list_imgs = []
        int_unit = int(255 / (num_total + 1))
        for index in range(1, num_total + 1):
            thresh = int_unit * index
            im_thresh = mvlib.filters.threshold(im_arr, thresh)
            list_imgs.append(im_thresh)
        return list_imgs

    def accepted(self):
        im_arr = self.get_image()
        if self.check_format(im_arr):
            list_imgs = self.processing(im_arr)
            # 将canvas::tabviewer的成员从Scroll转换为Grib
            canvas = g.get("canvas")
            canvas.stack2grib(self.paras["nRow"], self.paras["nColumn"])
            grib = canvas.currentWidget()
            grib.set_image(list_imgs)
            self.update_canvas()


class SplitRGB(Filter):
    title = "Split RGB Channels"
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.split({im})"

    def processing(self, im_arr):
        # return mvlib.color.split(im_arr)
        list_splits = mvlib.color.split(im_arr)
        list_splits.append(im_arr)
        return list_splits

    def run(self):
        im_arr = self.get_image()
        if self.check_format(im_arr):
            list_rgb = self.processing(im_arr)
            # 将canvas::tabviewer的成员从Scroll转换为Grib
            canvas = g.get("canvas")
            canvas.stack2grib(2, 2)
            grib = canvas.currentWidget()
            grib.set_image(list_rgb)


# ============= RGB - HSV ============
class RGB2HSV(Filter):
    title = 'RGB To HSV'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2hsv({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2hsv(im_arr)


class HSV2RGB(Filter):
    title = 'HSV To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.hsv2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.hsv2rgb(im_arr)

# ============= RGB - YUV ============
class RGB2YUV(Filter):
    title = 'RGB To YUV'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2yuv({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2yuv(im_arr)


class YUV2RGB(Filter):
    title = 'YUV To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.yuv2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.yuv2rgb(im_arr)

"""
# ============= RGB - CIE ============
class RGB2CIE(Filter):
    title = 'RGB To CIERGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2rgbcie({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2rgbcie(im_arr)

class CIE2RGB(Filter):
    title = 'CIERGB To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgbcie2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.rgbcie2rgb(im_arr)

# ============= RGB - LUV ============
class RGB2LUV(Filter):
    title = 'RGB To LUV'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2luv({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2luv(im_arr)

class LUV2RGB(Filter):
    title = 'LUV To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.luv2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.luv2rgb(im_arr)
"""

# ============= RGB - Lab ============
class RGB2Lab(Filter):
    title = 'RGB To Lab'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2lab({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2lab(im_arr)

class Lab2RGB(Filter):
    title = 'Lab To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.lab2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.lab2rgb(im_arr)

# ============= RGB - XYZ ============
class RGB2XYZ(Filter):
    title = 'RGB To XYZ'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.rgb2xyz({im})"

    def processing(self, im_arr):
        return mvlib.color.rgb2xyz(im_arr)

class XYZ2RGB(Filter):
    title = 'XYZ To RGB'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.color.xyz2rgb({im})"

    def processing(self, im_arr):
        return mvlib.color.xyz2rgb(im_arr)
