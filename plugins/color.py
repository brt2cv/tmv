# from PyQt5.QtWidgets import QMessageBox
from core.plugin import DialogFilter

def export_plugin(cls):
    return eval(cls)


class Gray(DialogFilter):
    title = 'Gray'
    features = {
        "mode": "rgb",
        "dtype": "uint8"
    }

    def processing(self, ips):
        from mvlib.color import rgb2gray
        gray = rgb2gray(ips)
        return gray

    def run(self):
        print("This is a plugin with dilog.")
        self.resize(300, 200)
        # self.move(0, 20)
        super().run()
