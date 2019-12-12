from util.expy import path_append
path_append("runtime", __file__)

import hid
import numpy as np
from time import sleep
from threading import Thread, Event

from util.base import Deletable
from util.log import make_logger
logger = make_logger(1)

BLOCK_TIMEOUT = 0.5
BLOCK_TIMEOUT_ms = BLOCK_TIMEOUT * 1000
HID_PACK_LEN = 64
BYTES_PACK_HEAD = bytes([0x80, 0x2e, 0x2e, 0x80])
BYTES_PACK_TAIL = bytes([0x2e, 0x80, 0x80, 0x2e])

HEROSYS_HID_DEVICE_PROTOCAL = {
    "PARA_ACTION_SENSOR_ADJ": 1<<7,
    "PARA_ACTION_LED_PWM": 1<<9,
#####################################################################
    "ExposureTimeSet": ((0xff<<0)|(0x11<<8)),  # 传感器曝光
    "OV9281GrobalGain": ((0xff<<0)|(0xC8<<8)),  # 传感器增益
    "LightLED_PWM_SET": ((0xff)|(0x04<<8)),  # 补光灯亮度
    "ExtraLED_PWM_SET": ((0xff)|(0x15<<8)),  # 外扩LED亮度
    "DecodeBuzzerSET": (1<<14),  # 下位机解码成功
}

HEROSYS_HID_DEVICE_CMD = {
    "GetParamData": [46, 128, 128, 46, 82, 101, 97, 100],
    "SetDecodeBuzzer": [0x7e, 0, 0x0a, 0x21, 0, 0, 0, 0x07, 0x54],
}

BYTE_ORDER = "little"
INT_SIZE = 4

def bytes2uint(bytes_):
    return int.from_bytes(bytes_, BYTE_ORDER)

def bytes2sint(bytes_):
    return int.from_bytes(bytes_, BYTE_ORDER, signed=True)

def uint2bytes(nInt):
    return nInt.to_bytes(INT_SIZE, BYTE_ORDER)

def sint2bytes(nInt):
    return nInt.to_bytes(INT_SIZE, BYTE_ORDER, signed=True)

def _int2uint(nInt):
    np_uint = np.uint32(nInt)
    return int(np_uint)

def list2pack(list_):
    """ 用于补充数据至65位 """
    # 写入时，包长为65：1位ID+64位数据
    len_list = len(list_)
    if len_list > HID_PACK_LEN:
        pass
        # yield list_[:64]
        # return list2pack(list_[64:])  # 递归
    else:
        len_remain = HID_PACK_LEN - len_list
        print(len_remain)
        return list_ + [0]*len_remain

def extract_img(bytes_data: bytearray):
    if isinstance(bytes_data, bytes):
        bytes_data = bytearray(bytes_data)
    barcode_len = bytes2uint(bytes_data[8:10])
    # img_size = bytes2uint(bytes_data[16:20])
    img_width = bytes2uint(bytes_data[12:14])
    img_height = bytes2uint(bytes_data[14:16])

#     logger.debug(f"""barcode_len: {barcode_len}
# img_width: {img_width}
# img_height: {img_height}
# """)

    start = HID_PACK_LEN +256 + barcode_len
    end = start + img_height * img_width
    img_data = bytes_data[start:end]

    img = np.asarray(img_data, dtype=np.uint8)  # img = bytes2ndarray(bytes_img)
    img = img.reshape(img_height, img_width)
    return img

def check_vendor(vid):
    vids = set()
    for d in hid.enumerate():
        vids.add(d["vendor_id"])
    bool_ = vid in vids
    return bool_

class HerosysHidDevice(Deletable):
    VID = 0xBACF  # 47823
    PID = 0xBDDC  # 48604

    def __init__(self):
        super().__init__()
        self._import_crc32()

        self.hid_io = hid.device()
        self.hid_params = None

        self.disconnected = Event()
        self.disconnected.set()

        self.monitor_init()

    def _import_crc32(self):
        NoCheck, CheckByDLL, CheckByPython = range(3)
        self.crc_method = CheckByPython  # you can change it as the way to check crc32

        if self.crc_method == CheckByDLL:
            return

        elif self.crc_method == CheckByDLL:
            import ctypes
            import os.path

            path_lib_crc = os.path.join(os.path.dirname(__file__), "runtime/libcrc.dll")
            self.lib_crc = ctypes.CDLL(path_lib_crc)

        else:  # self.crc_method == CheckByPython:
            from .crc import crc32
            self.module_crc = crc32
            # from importlib import import_module
            # self.module_crc = import_module(".crc.crc32", __package__)

    def _check_crc32(self, byte_value, byte_array, length, offset=0):
        """ return True or False """
        if self.crc_method == 0:  # NoCheck
            return True
        elif self.crc_method == 1:  # CheckByDLL
            value = bytes2sint(byte_value)

        else:  # self.crc_method == CheckByPython:
            value = bytes2uint(byte_value)

        crc_value = self._crc32(byte_array, length, offset)
        # logger.debug(f"crc32校验码: {value}, crc计算值: {crc_value}")
        return crc_value == value

    def _crc32(self, byte_array, length, offset=0):
        if self.crc_method == 0:  # NoCheck
            return 0

        elif self.crc_method == 1:  # CheckByDLL
            if isinstance(byte_array, bytearray):
                byte_array = bytes(byte_array)

            if offset:
                crc_value = self.lib_crc.crc32_offset(byte_array, length, offset)
            else:
                crc_value = self.lib_crc.crc32(byte_array, length)

        else:  # CheckByPython
            crc_value = self.module_crc.crc32(byte_array, length, offset)

        return crc_value

    def _hid_open(self):
        self.hid_io.open(self.VID, self.PID)
        self.hid_info()
        # self.hid_io.set_nonblocking(True)
        self._send_command(HEROSYS_HID_DEVICE_CMD["GetParamData"])

    def monitor_init(self):
        """ 热插拔的监听 """
        period = BLOCK_TIMEOUT
        self.monitorRunning = Event()
        self.monitorRunning.set()

        def monitor_hjhid():
            while self.monitorRunning.is_set():
                if check_vendor(self.VID):
                    logger.debug("监听到合杰HID接入")
                    self._hid_open()
                    self.disconnected.clear()

                    self.disconnected.wait()  # 阻塞监听
                else:
                    sleep(period)

        # 进入热插拔监听
        self.tid_monitor = Thread(target=monitor_hjhid)
        self.tid_monitor.setDaemon(True)
        self.tid_monitor.start()

    def monitor_stop(self):
        self.monitorRunning.clear()

    def destroy(self):
        super().destroy()
        self.monitor_stop()
        logger.debug("回收HID监听线程...")
        self.disconnected.set()  # 终止连接状态时监听线程的Event阻塞
        self.tid_monitor.join(0)

        logger.debug("关闭合杰HID设备")
        self.hid_io.close()

    def hid_info(self):
        print("Manufacturer: %s" % self.hid_io.get_manufacturer_string())
        print("Product: %s" % self.hid_io.get_product_string())
        print("Serial No: %s" % self.hid_io.get_serial_number_string())

    def read(self):
        """ 阻塞读取消息，如果调用者的读取偏慢，可能导致丢失数据
            raise OSError when read-error.
        """
        if self.disconnected.is_set():
            sleep(BLOCK_TIMEOUT)
            return None

        bytes_data = bytearray()
        while True:
            try:
                pack = self.hid_io.read(HID_PACK_LEN, timeout_ms=BLOCK_TIMEOUT_ms)
            except (OSError, ValueError) as e:
                logger.debug("合杰HID设备已断开连接")
                self.disconnected.set()
                self.hid_params = None
                # self.hid_head = None
                return None

            if not pack:
                if bytes_data:  continue
                else:  break
            pack = bytearray(pack)

            index = pack.find(BYTES_PACK_TAIL)
            if index < 0:
                bytes_data += pack
            else:
                bytes_data += pack[:index+4]
                # BYTES_PACK_TAIL可能出现在两个64位包直接
                # 理应查找……这里直接忽略
                break

            # 最大包长检测（如果一直未收到有效结束符）……忽略

        # check header
        if bytes_data and bytes_data[:4] != BYTES_PACK_HEAD:
            logger.debug(f"非法的HID数据头：【{bytes(bytes_data[:10])}】")
            return None
            # 尝试二次查找有效数据……这里忽略
            # offset = bytes_data.find(BYTES_PACK_HEAD)
            # if offset > 0:
            #     logger.debug("已修复数据包")
            #     bytes_data = bytes_data[offset:]
            #     return bytes_data

        if bytes_data:
            # 校验包头
            crc32_value = self._check_crc32(bytes_data[4:8], bytes_data, 64, 8)
            # assert crc32_value, "crc校验错误"
            crc32_para = self._check_crc32(bytes_data[28:32], bytes_data[64: 64+256], 256)
            # assert crc32_para, "crc校验错误"
            if not crc32_para or not crc32_value:
                logger.error("crc校验错误，舍弃HID包数据")
                return None

        logger.debug(f"获取到HID数据，Length：【{len(bytes_data)}】")
        if self.hid_params is None:
            # 获取【参数区】数据
            self.hid_head = bytearray(bytes_data[:64])  # 固定的头格式
            self.hid_params = bytearray(bytes_data[64: 64+256])  # 返回【参数区】数据

        return bytes_data

    # def _send_params(self, a, b, action):
    #     if self.hid_params is None:
    #         logger.warning("尚未接收到参数区数据，指令发送失败")
    #         return

    #     a = uint2bytes(a)

    #     self.hid_params[a & 0x00ff] = (self.hid_params[a & 0x00ff] & _int2uint(~(a & 0x00ff))) | _int2uint(b)

    #     self.hid_head[0:4] = [128, 46, 46, 128]  # 802e2e80
    #     self.hid_head[24:28] = uint2bytes(1)  # DataSwitch
    #     self.hid_head[32:36] = uint2bytes(action)  # ParaAction

    #     ParaCrc32 = self.lib_crc.crc32_value(bytes(self.hid_params), 256)
    #     # ParaCrc32 = crc32_value(self.hid_params, 256)
    #     self.hid_head[28:32] = uint2bytes(_int2uint(ParaCrc32))  # ParaCrc32
    #     crc32_value = self.lib_crc.crc32_offset(bytes(self.hid_head), 64, 8)
    #     # crc32_value = crc32_value(self.hid_head, 64, 8)
    #     self.hid_head[4:8] = uint2bytes(_int2uint(crc32_value))

    #     self.hid_io.write(b"0" + self.hid_head + self.hid_params)

    # def _send_params_ex(self, a, b, action):
    #     """ 尝试将整个组包过程通过C代码实现 """
    #     if self.hid_params is None:
    #         logger.warning("尚未接收到参数区数据，指令发送失败")
    #         return

    #     bytes_cmd = self.lib_hidcmd.make_command(
    #         self.hid_head,
    #         self.hid_params,
    #         a, b, action
    #     )
    #     print("Total cmd length >> ", len(bytes_cmd))
    #     self.hid_head = bytes_cmd[:64]
    #     self.hid_params = bytes_cmd[64:]

    #     self.hid_io.write(bytes_cmd)

    def set_exposure(self, value):
        """ 传感器曝光: [0, 256] """
        a = HEROSYS_HID_DEVICE_PROTOCAL["ExposureTimeSet"]
        action = HEROSYS_HID_DEVICE_PROTOCAL["PARA_ACTION_SENSOR_ADJ"]
        self._send_params(a, value, action)

    def set_gain(self, value):
        """ 传感器增益: [0, 256] """
        a = HEROSYS_HID_DEVICE_PROTOCAL["OV9281GrobalGain"]
        action = HEROSYS_HID_DEVICE_PROTOCAL["PARA_ACTION_SENSOR_ADJ"]
        self._send_params(a, value, action)

    def set_led_light(self, value):
        """ 补光灯亮度: [0, 255] """
        a = HEROSYS_HID_DEVICE_PROTOCAL["LightLED_PWM_SET"]
        action = HEROSYS_HID_DEVICE_PROTOCAL["PARA_ACTION_LED_PWM"]
        self._send_params(a, value, action)

    def set_ledex_light(self, value):
        """ 外扩LED亮度: [0, 255] """
        a = HEROSYS_HID_DEVICE_PROTOCAL["ExtraLED_PWM_SET"]
        action = 0
        self._send_params(a, value, action)


    def _send_command(self, byte_array):
        # cmd_id = b"0"  # HID协议的Msg-ID（即，实际发送了65Bytes的HID包）
        self.hid_io.write(b"0" + bytes(byte_array))  # b"0" is a serial number

    def _send_params(self, action):
        if self.hid_params is None:
            logger.warning("尚未接收到参数区数据，指令发送失败")
            return

        logger.debug(f"验证当前 len(head): {len(self.hid_head)}, len(params): {len(self.hid_params)}")

        self.hid_head[0:4] = [128, 46, 46, 128]  # 802e2e80
        self.hid_head[24:28] = uint2bytes(1)  # DataSwitch
        self.hid_head[32:36] = uint2bytes(action)  # ParaAction

        ParaCrc32 = self._crc32(bytes(self.hid_params), 256)
        self.hid_head[28:32] = list(uint2bytes(ParaCrc32))  # ParaCrc32
        # logger.debug(f"para32 计算值: {ParaCrc32}, 编码: {self.hid_head[28:32]}")

        crc32_value = self._crc32(bytes(self.hid_head), 64, 8)
        self.hid_head[4:8] = list(uint2bytes(crc32_value))
        # logger.debug(f"crc32_value 计算值: {ParaCrc32}, 编码: {self.hid_head[4:8]}")

        cmd_array = self.hid_head + self.hid_params + bytearray([0x2e, 0x80, 0x80, 0x2e])
        self.hid_io.write(b"0" + bytes(cmd_array))

    def set_alarm_by_para(self):
        """ 通过参数区传入动作参数 """

    def cmd_alarm(self):
        self._send_command(HEROSYS_HID_DEVICE_CMD["SetDecodeBuzzer"])

        # 或者使用参数区控制声音反馈：
        # logger.debug("正在通过para控制alarm反馈")
        # self._send_params(HEROSYS_HID_DEVICE_PROTOCAL["DecodeBuzzerSET"])


if __name__ == "__main__":
    from time import sleep

    state = check_vendor(HerosysHidDevice.VID)
    print("check_vendor >>>", state)

    device = HerosysHidDevice()
    # def signal(time):
    #     print(f"已连接 @{time}")
    # device.open(callback=signal, args=("10:12",))

    sleep(1)  # 等待
    n = 2
    while n:
        data = device.read()
        len_ = len(data) if data else 0
        print(f"接收到数据：{len_}")
        n -= 1
    # extract_img(data)

    for i in range(1):
        device.cmd_alarm()
        sleep(0.1)

    print("1s后将终止程序")
    sleep(1)
    device.destroy()
    print("End")
