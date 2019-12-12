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
        declare_member("snap", asarray(self).copy())  # 图像快照
        declare_member("roi")
        declare_member("msk")  # 由选区自动生成
        declare_member("lut")  # 索引表
        declare_member("mark")
        declare_member("contours", [])

    # def _copy_meta(self, meta):
    #     """ Make a 2-level deep copy of the meta dictionary.
    #     """
    #     # self._meta = Dict()
    #     # for key, val in meta.items():
    #     #     if isinstance(val, dict):
    #     #         val = Dict(val)  # Copy this level
    #     #     self._meta[key] = val
    #     self._meta = meta

    def take_snap(self):
        self._meta["snap"] = asarray(self).copy()

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

    def get_snap(self):
        snapshot = self._meta["snap"]
        return snapshot

    def reset(self):
        """ 使用快照恢复图像 """
        snapshot = self._meta["snap"]
        # if snapshot is not None:
        #     if msk and not self.get_msk('out') is None:
        #         msk = self.get_msk('out')
        #         self.imgs[self.cur][msk] = self.snap[msk]
        #     else:
        #         self.imgs[self.cur][:] = self.snap
        return ImagePlus(snapshot, self._meta)

    # def swap(self):
    #     """ 交换快照和前景 """
    #     print(type(self.snap), type(self.imgs[self.cur]), self.cur)
    #     if self.snap is None:return
    #     if isinstance(self.imgs, list):
    #         self.snap, self.imgs[self.cur] = self.imgs[self.cur], self.snap
    #     else:
    #         buf = self.img.copy()
    #         self.img[:], self.snap[:] = self.snap, buf

if __name__ == "__main__":
    im = np.zeros([3, 4])
    ips = ImagePlus(im, {"a":123, "b":234})

    # 经过asarray()后的im，丢失meta属性，类型恢复为
    im2 = asarray(ips)
    print(">> type of asarray(ips): ", type(im2))

    # 简单的np.ndarray操作也会替换源对象
    ips2 = ips.reshape([4,3])
    print(">> type of asarray(ips): ", type(ips2))

    ips[0][0] = 1
    print("ips.view: ", ips)
    print("ips.meta: ", ips._meta)

    ips = ips.reset()
    print("ips_reset.view: ", ips)
