
if __name__ == "__main__":
    import ctypes

    crc_dll = ctypes.CDLL("../runtime/libcrc.dll")  # the same as: ctypes.cdll.LoadLibrary
    # help(crc_dll)
    data = b"1234567890wrdpjqzuy:ahtsfbneioxvcgkml,."
    offset = 1
    len_ = len(data) - offset
    val_crc = crc_dll.crc32(data, len_, offset)
    print("crc >> ", val_crc)
