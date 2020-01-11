from utils.imgio import guess_mode
from mvlib.backend import include, get_backend
from .. import alert

class FormatTypeError(Exception):
    """ IpsFormat设定的属性与当前处理图像不符 """


class IpsFormat:
    mode2str = {
        "L": "gray",
        "RGB": "rgb",
        "RGBAE": "rgba"
    }
    prop_choices = {
        "mode": {"gray", "rgb", "rgba"},
        "dtype": {"uint8", "uint16", "uint32", "uint64", "float"},
        "backend": {"pillow", "numpy", "opencv", "scipy", "skimage"}
    }

    def __init__(self, properties: dict):
        """
        Example of properties: {
            "mode": "gray",
            "dtype": "uint8",
            "require": {"roi", ... },
        }
        """
        for key, value in properties.items():
            assert key in self.prop_choices, f"未知的属性项: 【{key}】"
            # 区分不同类型的value: str, enum(int), list, tuple, set, dict
            if type(value) is str:  # in {str, int, float}:
                assert value in self.prop_choices[key], f"未知的{key}: 【{value}】"
            elif type(value) is set:  # collections.abc.Collection, 但str也属于该类型
                diff = value - self.prop_choices[key]
                assert not diff, f"未知的choice: 【{diff}】"
            else:
                raise Exception("尚不支持的数据类型")
        self.property = properties

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
            warning = f'dtype error: 【{dtype}】 image is required, current image is 【{im_arr.dtype}】'
            alert(warning)
            raise FormatTypeError(warning)
            # return

        backend = self.property.get("backend")
        if backend and not include(backend):
            curr_backend = get_backend()
            warning = f"Backend error: 【{backend}】is required, current backend is 【{curr_backend}】"
            alert(warning)
            raise FormatTypeError(warning)

        return True
