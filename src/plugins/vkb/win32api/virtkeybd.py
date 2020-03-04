PAUSE_TIME = 0.05

import os.path
from site import addsitedir
site_dir = os.path.join(os.path.dirname(__file__), 'runtime')
addsitedir(site_dir)

from time import sleep

import win32api
import win32con
import win32clipboard

def copy(text):
    win32clipboard.OpenClipboard()
    # win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()

def keybd_paste():
    # win32api.keybd_event(16470, 0, 0, 0)  # Ctrl+V # 无效
    win32api.keybd_event(17, 0, 0, 0)  # ctrl
    win32api.keybd_event(86, 0, 0, 0)  # v
    sleep(PAUSE_TIME)
    # win32api.keybd_event(16470 , 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

def keybd_output(text, withEnter=False):
    copy(text)
    keybd_paste()

    if withEnter:
        win32api.keybd_event(13, 0, 0, 0)
        sleep(PAUSE_TIME)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
