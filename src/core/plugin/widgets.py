from utils.qt5wx.wx_unit import *

class TplWidgetsManager:

    def __init__(self, parent):
        self.parent = parent

    def parse_elem(self, dict_elem):
        """
        {
            "type": "slider",
            "val_range": [0, 100]
            ...
        }
        """
        types = {
            "edit":     self.make_edit,
            "slider":   self.make_slider,
            "spinbox":  self.make_spinbox,
            "radio":    self.make_radio,
        }

        wx_type = dict_elem["type"]
        if wx_type not in types:
            raise Exception(f"未知的控件模板类型：【{wx_type}】")
        func = types[wx_type]
        return func(dict_elem)

    # def get_params(self):
    #     name = dict_elem.get("name", "")
    #     val_init = dict_elem.get("val_init", 0)
    #     val_range = dict_elem.get("val_range", [0, 100])
    #     isCheckbox = dict_elem.get("isCheckbox", True)
    #     isChecked = dict_elem.get("isChecked", False)

    def make_edit(self, dict_elem):
        wx = UnitLineEdit(
                self.parent,
                dict_elem.get("name", ""),
                dict_elem.get("val_init", 0),
                dict_elem.get("isCheckbox", True),
                dict_elem.get("isChecked", False)
            )
        return wx

    def make_slider(self, dict_elem):
        wx = UnitSlider(
                self.parent,
                dict_elem.get("name", ""),
                dict_elem.get("val_range", [0, 100]),
                dict_elem.get("val_init", 0),
                dict_elem.get("showValue", True),
                dict_elem.get("isCheckbox", True),
                dict_elem.get("isChecked", False)
            )
        return wx

    def make_spinbox(self, dict_elem):
        wx = UnitSpinbox(
                self.parent,
                dict_elem.get("name", ""),
                dict_elem.get("val_range", [0, 100]),
                dict_elem.get("val_init", 0),
                dict_elem.get("isCheckbox", True),
                dict_elem.get("isChecked", False)
            )
        return wx

    def make_radio(self, dict_elem):
        """ radio 选项 """
        wx = UnitRadio(
                self.parent,
                dict_elem.get("name", ""),
                dict_elem["val_range"],
                dict_elem.get("val_init", 0),
                # dict_elem.get("isCheckbox", True),
                # dict_elem.get("isChecked", False)
            )
        return wx
