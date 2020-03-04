from time import sleep

from utils.expy import path_expand
from utils.base import rpath2curr
path_expand(rpath2curr("env"))

import pyperclip
try:
    from .virtkey import press_keycode, release_keycode
except:  # linux
    pass

PAUSE_TIME = 0.05  # 本机测试 0.01 有效


def keybd_output(text, withEnter=False):
    pyperclip.copy(text)
    # clip_text = pyperclip.paste()
    press_keycode(0x1D)
    press_keycode(0x2F)
    sleep(PAUSE_TIME)
    release_keycode(0x2F)
    release_keycode(0x1D)

    if withEnter:
        press_keycode(0x1C)
        sleep(PAUSE_TIME)
        release_keycode(0x1C)


if __name__ == "__main__":
    sleep(1)
    keybd_output("abcdefg", 1)
