# from PyQt5.QtWidgets import QMessageBox
from core.plugin.filter import Filter, DialogFilter

class Gray(Filter):
    title = 'Gray'
    features = {
        "mode": "rgb",
        "dtype": "uint8"
    }

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
