from utils.imgio import guess_mode
from .. import alert

class FormatTypeError(Exception):
    """ IpsFormat设定的属性与当前处理图像不符 """


class IpsFormat:
    mode2str = {
        "L": "gray",
        "RGB": "rgb",
        "RGBAE": "rgba"
    }

    def __init__(self, properties: dict):
        """
        Example of properties: {
            "mode": "gray",
            "dtype": "uint8",
            "require": {"roi", ... },
        }
        """
        self.property = {}
        for key, value in properties.items():
            if key == "mode":  self.set_mode(value)
            elif key == "dtype":  self.set_dtype(value)
            elif key == "require":  self.set_require(value)
            else:  raise Exception(f"未知的属性项: 【{key}】")

    def set_mode(self, mode):
        choices = {"gray", "rgb", "rgba"}
        assert mode in choices, f"未知的mode: 【{mode}】"
        self.property["mode"] = mode

    def set_dtype(self, dtype):
        choices = {"uint8", "uint16", "uint32", "uint64", "float"}
        assert dtype in choices, f"未知的dtype: 【{dtype}】"
        self.property["dtype"] = dtype

    def set_require(self, set_req):
        choices = {"roi"}
        diff = choices - set_req
        assert not diff, f"未知的requirement: 【{diff}】"
        self.property["require"] = set_req

    def tolist(self):
        """ 用于转换为ImagePy::Filter::note格式 """

    def check(self, im_arr):
        """ return True if OK """
        if im_arr is None:
            warning = 'No image selected!'
            alert(warning)
            raise FormatTypeError(warning)
            # return

        mode = self.property.get("mode")
        if mode:
            curr_mode = self.mode2str[guess_mode(im_arr)]
            if mode != curr_mode:
                warning = f'Mode error: 【{mode}】 image is required, current image is 【{curr_mode}】'
                alert(warning)
                raise FormatTypeError(warning)
                # return

        dtype = self.property.get("dtype")
        if dtype and dtype != im_arr.dtype:
            warning = f'Dtype error: 【{dtype}】 image is required, current image is 【{im_arr.dtype}】'
            alert(warning)
            raise FormatTypeError(warning)
            # return

        return True
