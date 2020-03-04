import win32clipboard
import win32con
import win32api


def get_clip_text():
    win32clipboard.OpenClipboard()
    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return text

def set_clip_text(string):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, string)
    win32clipboard.CloseClipboard()

copy = set_clip_text
paste = get_clip_text


if __name__ == '__main__':
    from time import sleep
    sleep(1)

    set_clip_text("abcd")

    # 自动粘贴剪切板中的内容  
    # win32api.keybd_event(16470, 0, 0, 0)  # ctrl+v # 无效
    win32api.keybd_event(17, 0, 0, 0)  # ctrl
    win32api.keybd_event(86, 0, 0, 0)  # v
    sleep(0.01)
    # win32api.keybd_event(16470 , 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

    # win32api.keybd_event(13, 0, 0, 0)  # Enter
    # win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
