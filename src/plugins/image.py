import mvlib
from core.plugin.filter import DialogFilter

class ResizeImage(DialogFilter):
    title = "Resize Image"
    view = [{
        "type": "edit",
        "name": "width  ",
        "isCheckbox": False,
        "para": "width"
    },{
        "type": "edit",
        "name": "height ",
        "isCheckbox": False,
        "para": "height"
    }]
    scripts = "{output} = mvlib.transform.resize({im}, {size})"

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def processing(self, im_arr):
        width = int(self.paras["width"])
        height = int(self.paras["height"])
        self.paras["size"] = [height, width]  # commit scripts para
        return mvlib.transform.resize(im_arr, self.paras["size"])

    def run(self):
        ips = self.get_image()
        h, w = ips.shape[:2]
        self.view[0]["val_init"] = w
        self.view[1]["val_init"] = h
        # if self.view[0]["type"] == "slider":
        #     self.view[0]["val_range"] = [0, w]
        #     self.view[1]["val_range"] = [0, h]
        super().run()


class RescaleImage(DialogFilter):
    title = "Rescale Image"
    view = [{
        "type": "edit",
        "name": "比例 ",
        # "val_range": [-180, 180],
        "para": "scale"
    }]

    def processing(self, im_arr):
        return mvlib.transform.rescale(im_arr, self.paras["scale"])


# class FlipImage(DialogFilter):
#     title = "Rotate Image"
#     view = [{
#         "type": "radio",
#         "name": "选项 ",
#         "val_range": ["水平", "垂直"],
#         "para": "orientation"
#     }]

#     def processing(self, im_arr):
#         return mvlib.transform.rotate(im_arr, self.paras["angle"])


class RotateImage(DialogFilter):
    title = "Rotate Image"
    view = [{
        "type": "slider",
        "name": "angle ",
        "val_range": [-180, 180],
        "para": "angle"
    }]

    def processing(self, im_arr):
        return mvlib.transform.rotate(im_arr, self.paras["angle"])


# class Projection(DialogFilter):
#     title = "图像投影"
#     view = [{
#         "type": "slider",
#         "name": "angle ",
#         "val_range": [-180, 180],
#         "para": "angle"
#     }]

#     def processing(self, im_arr):
#         return mvlib.transform.rotate(im_arr, self.paras["angle"])


# class AffineImage(DialogFilter):
#     title = "Rotate Image"
#     view = [{
#         "type": "slider",
#         "name": "angle ",
#         "val_range": [-180, 180],
#         "para": "angle"
#     }]

#     def processing(self, im_arr):
#         return mvlib.transform.rotate(im_arr, self.paras["angle"])
