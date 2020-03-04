import pyperclip

from time import sleep
sleep(1)

pyperclip.copy("docs.python.org")
clip_text = pyperclip.paste()  # 输出
print("获取到粘贴板字符 >> ", clip_text)