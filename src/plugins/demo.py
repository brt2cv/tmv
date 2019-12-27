from core.plugin.filter import PreviewFilter

class DemoDlg(PreviewFilter):
    features = {
        "mode": "rgb",
        "dtype": "uint8"
    }

    def processing(self, im_arr):
        from mvlib.color import rgb2gray
        gray = rgb2gray(im_arr)
        return gray

    def run(self):
        print("This is a plugin with dilog.")
        self.resize(300, 200)
        # self.move(0, 20)
        super().run()
