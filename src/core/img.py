import numpy as np
from imageio.core.util import Array, asarray

# asarray = np.asarray

class ImagePlus(Array):
    """ ArrayPlus(array, meta=None)

    A subclass of np.ndarray that has a meta attribute. Get the dictionary
    that contains the meta data using ``im.meta``. Convert to a plain numpy
    array using ``np.asarray(im)``.

    """
    # def __new__(cls, array, meta=None):
    #     # Check
    #     if not isinstance(array, np.ndarray):
    #         raise ValueError("Array expects a numpy array.")
    #     if not (meta is None or isinstance(meta, dict)):
    #         raise ValueError("Array expects meta data to be a dict.")
    #     # Convert and return
    #     meta = meta if meta is not None else {}
    #     try:
    #         ob = array.view(cls)
    #     except AttributeError:  # pragma: no cover
    #         # Just return the original; no metadata on the array in Pypy!
    #         return array
    #     ob._copy_meta(meta)
    #     return ob

    def __init__(self, array, meta=None):
        def declare_member(name, value=None):
            if name not in self._meta:
                self._meta[name] = value
        # declare_member("snap", asarray(self).copy())
        declare_member("roi")
        declare_member("mask")  # 由选区自动生成
        declare_member("contours", [])

    def _copy_meta(self, meta):
        """ Make a 2-level deep copy of the meta dictionary.
        """
        # self._meta = Dict()
        # for key, val in meta.items():
        #     if isinstance(val, dict):
        #         val = Dict(val)  # Copy this level
        #     self._meta[key] = val
        self._meta = meta

    # @property
    # def mode(self):
    #     return guess_mode(self)

    # def get_msk(self, mode='in'):
    #     if self.roi==None:return None
    #     if self.msk is None:
    #         self.msk = np.zeros(self.size, dtype=np.bool)
    #     if self.roi.update or mode!=self.mskmode:
    #         self.msk[:] = 0
    #         if isinstance(mode, int):
    #             self.roi.sketch(self.msk, w=mode, color=True)
    #         else: self.roi.fill(self.msk, color=True)
    #         if mode=='out':self.msk^=True
    #         self.roi.update = False
    #         self.mskmode=mode
    #     return self.msk


if __name__ == "__main__":
    im = np.zeros([3, 4])
    ips = ImagePlus(im, {"a":123, "b":234})

    # 经过asarray()后的im，丢失meta属性，类型恢复为
    im2 = asarray(ips)
    print(">> type of asarray(ips): ", type(im2))

    # 简单的np.ndarray操作也会替换源对象
    ips2 = ips.reshape([4,3])
    print(">> type of ips2: ", type(ips2))  # ImagePlus

    ips[0][0] = 1
    print("ips.view: ", ips)
    print("ips.meta: ", ips._meta)

    # copy()操作依旧可用
    ips3 = ips.copy()
    print(">> type of ips3: ", type(ips3))  # ImagePlus
    print(ips3.meta)


#####################################################################
from utils.imgio import imread
class ImageContainer:
    """ 用于图像的收发管理 """
    def get_image(self):
        """ 返回一张ndarry图像 """
        return self.im_arr

    def set_image(self, im_arr):
        """ 设值Canvas图像 """
        self.im_arr = im_arr

    def load_image(self, path_file):
        """ 对get_image()的简单封装 """
        im_arr = imread(path_file)
        self.set_image(im_arr)


# import numpy as np
from .undo import UndoStack
class ImageManager(ImageContainer):
    """ 用于图像的多版本管理，包括：
        * stack: 每次执行图像操作的processing（而不是存储快照）
        * snap: 用于存储origin图像，用于连续测试时获取原始图像

        目标：尽可能使其接口接近ImagePlus，无缝对接canvas
    """
    def __init__(self):
        self.curr = None  # ips
        self.snap = None  # ips
        self.stack = UndoStack()

    def take_snap(self):
        self.snap = None if self.curr is None else self.curr.copy()

    def reset(self):
        self.curr = self.snap.copy()

    def load_image(self, path_file):
        im_arr = imread(path_file)
        self.commit(im_arr)

    def get_image(self):
        return self.curr

    def get_snap(self):
        return self.snap

    def set_image(self, im_arr):
        """ 注意：Manager中set_image() 只是临时显示图像
            如确定存储图像，应使用commit()
        """
        assert isinstance(im_arr, np.ndarray), f"未识别的图像格式：【{type(im_arr)}】"
        if isinstance(im_arr, ImagePlus):
            self.curr = im_arr
        else:
            self.curr = ImagePlus(im_arr)

    def commit(self, im_arr):
        """ 类似set_image()，但会增加take_snap()操作，并写入UndoStack """
        self.set_image(im_arr)
        ips_prev = None if self.snap is None else self.snap.copy()
        cmd = ImgSnapCommand(ips_prev, self.curr.copy())
        self.stack.commit(cmd)
        self.take_snap()

    def undo(self):
        """ 撤销操作 """
        self.curr = self.stack.undo()
        self.take_snap()

    def redo(self):
        self.curr = self.stack.redo()
        self.take_snap()

    def history(self):
        """ 显示undostack列表 """

    def dumps(self):
        """ 导出commit的脚本形式 """


from .undo import UndoCommand
class ImgSnapCommand(UndoCommand):
    """ 功能仅限简单存储图像 """
    def __init__(self, ips_prev, ips_new):
        self.prev = ips_prev
        self.new = ips_new

    def execute(self):
        return self.new.copy()

    def rollback(self):
        return None if self.prev is None else self.prev.copy()
