# from PyQt5.QtWidgets import QMessageBox
from core.plugin.filter import Filter, DialogFilter, DialogFilterBase
from core import g

class Gray(Filter):
    title = 'Gray'
    formats = {"mode": "rgb"}
    scripts = "{output} = mvlib.rgb2gray({im})"

    def processing(self, im_arr):
        from mvlib.color import rgb2gray
        gray = rgb2gray(im_arr)
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
    scripts = "{output} = mvlib.threshold({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        from mvlib.filters import threshold
        return threshold(im_arr,
                         self.para["thresh"],
                         self.para["maxval"])


class ArithmeticThreshold(DialogFilterBase):
    """ 比例阈值 """
    title = "比例阈值"
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
        from mvlib.filters import threshold
        num_total = self.para["nRow"] * self.para["nColumn"]
        list_imgs = []
        int_unit = int(255 / (num_total + 1))
        for index in range(1, num_total + 1):
            thresh = int_unit * index
            im_thresh = threshold(im_arr, thresh)
            list_imgs.append(im_thresh)
        return list_imgs

    def accepted(self):
        try:
            im_arr = self.get_image()
            self.check_format(im_arr)

            list_imgs = self.processing(im_arr)
            # 将canvas::tabviewer的成员从Scroll转换为Grib
            canvas = g.get("canvas")
            canvas.stack2grib(self.para["nRow"], self.para["nColumn"])
            grib = canvas.currentWidget()
            grib.set_image(list_imgs)
            self.update_canvas()
        except Exception:
            pass


class SplitRGB(Filter):
    title = "Split RGB Channels"
    formats = {"mode": "rgb"}

    def processing(self, im_arr):
        from mvlib.color import split
        return split(im_arr)

    def run(self):
        im_arr = self.get_image()
        self.check_format(im_arr)

        list_rgb = self.processing(im_arr)
        # 将canvas::tabviewer的成员从Scroll转换为Grib
        canvas = g.get("canvas")
        canvas.stack2grib(2, 2)
        grib = canvas.currentWidget()
        grib.set_image(list_rgb)
