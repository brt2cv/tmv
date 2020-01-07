from core.plugin.filter import DialogFilter

class PluginForApp(DialogFilter):
    title = "App内部Plugin"
    buttons = ["close"]
    view = [{
        "type": "slider",
        "name": "参数  ",
        "val_init": 128,
        "val_range": [0, 255],
        "para": "thresh"
    },{
        "type": "slider",
        "name": "可选参数",
        "val_init": 255,
        "val_range": [0, 255],
        "isCheckbox": True,
        "para": "maxval"
    }]
    # para = {"thresh": 128, "maxval": 255}
    scripts = "{output} = mvlib.filters.threshold({im}, {thresh}, {maxval})"

    def processing(self, im_arr):
        print(">>>", self.paras["thresh"], self.paras["maxval"])

    def run(self):
        print("调用App内部插件")
        super().run()
