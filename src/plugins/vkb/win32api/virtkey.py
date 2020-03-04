import win32api
import win32con

from keysym import sym2code

class virtkey:
    def press_keycode(self, keycode):
        win32api.keybd_event(keycode,0,0,0)

    def release_keycode(self, keycode):
        win32api.keybd_event(keycode,0,win32con.KEYEVENTF_KEYUP,0)

    def press_symbol(self, symbol):
        code = sym2code[symbol]
        self.press_keycode(code)

    def release_symbol(self, symbol):
        code = sym2code[symbol]
        self.release_keycode(code)


# class POINT(Structure):
#   _fields_ = [("x", c_ulong),("y", c_ulong)]

# def get_mouse_point():
#   po = POINT()
#   windll.user32.GetCursorPos(byref(po))
#   return int(po.x), int(po.y)

# def mouse_click(x=None,y=None):
#   if not x is None and not y is None:
#     mouse_move(x,y)
#     time.sleep(0.05)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# def mouse_dclick(x=None,y=None):
#   if not x is None and not y is None:
#     mouse_move(x,y)
#     time.sleep(0.05)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
#   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# def mouse_move(x,y):
#   windll.user32.SetCursorPos(x, y)

# def key_input(str=''):
#   for c in str:
#     win32api.keybd_event(VK_CODE[c],0,0,0)
#     win32api.keybd_event(VK_CODE[c],0,win32con.KEYEVENTF_KEYUP,0)
#     time.sleep(0.01)


if __name__ == "__main__":
    from time import sleep

    key = virtkey()
    words = " HELLO WORD"

    for x in words:
        x = x.upper()

        key.press_symbol(x)
        key.release_symbol(x)

        sleep(0.5)
