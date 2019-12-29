# from PyQt5.QtWidgets import QMessageBox
from core.plugin.filter import Filter, DialogFilter
from core import g

class Gray(Filter):
    title = 'Gray'
    features = {
        "mode": "rgb",
        "dtype": "uint8"
    }
    scripts = "{output} = mvlib.rgb2gray({im})"

    def processing(self, im_arr):
        from mvlib.color import rgb2gray
        gray = rgb2gray(im_arr)
        return gray


class Threshold(DialogFilter):
    title = "Threshold"
    features = {
        "mode": "gray"
    }
    view = [{
        "type": "slider",
        "name": "阈值",
        "val_init": 128,
        "val_range": [0, 255],
        "isCheckbox": False,
        "para": "thresh"
    },{
        "type": "slider",
        "name": "阈值2",
        "val_init": 255,
        "val_range": [0, 255],
        "isCheckbox": False,
        "para": "maxval"
    }]
    # para = {"thresh": 128, "maxval": 255}
    scripts = "{output} = mvlib.threshold({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        from mvlib.filters import threshold
        return threshold(im_arr,
                         self.para["thresh"],
                         self.para["maxval"])

    def run(self):
        print("This is a plugin with dilog.")
        self.resize(400, 0)
        # self.move(0, 20)
        super().run()


class SplitRGB(Filter):
    title = 'Split RGB Channels'
    features = {"mode": "rgb"}

    def processing(self, im_arr):
        from mvlib.color import split
        return split(im_arr)

    def run(self):
        im_arr = self.get_image()
        self.check_features(im_arr)

        list_rgb = self.processing(im_arr)
        # 将canvas::tabviewer的成员从Scroll转换为Grib
        canvas = g.get("canvas")
        canvas.stack2grib(2, 2)
        grib = canvas.currentWidget()
        grib.set_image(list_rgb)
