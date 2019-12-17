from core.plugin import DialogFilter

def export_plugin(cls=None):  # cls并不建议直接提供默认值'DemoDlg'
    if cls is None:
        cls = "DemoDlg"
    return eval(cls)

class DemoDlg(DialogFilter):
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
