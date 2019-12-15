from util.imgio import guess_mode
from .. import utils

class FeatureTypeError(Exception):
    """ IpsFeature设定的属性与当前处理图像不符 """


class IpsFeature:
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

    def check(self, ips):
        """ return True if OK """
        if ips is None:
            warning = 'No image selected!'
            utils.alert(warning)
            raise FeatureTypeError(warning)
            # return

        mode = self.property.get("mode")
        if mode and mode != guess_mode(ips):
            warning = f'Mode error: 【{mode}】 image is required'
            utils.alert(warning)
            raise FeatureTypeError(warning)
            # return

        dtype = self.property.get("dtype")
        if dtype and dtype != ips.dtype:
            warning = f'Dtype error: 【{dtype}】 image is required'
            utils.alert(warning)
            raise FeatureTypeError(warning)
            # return

        return True
