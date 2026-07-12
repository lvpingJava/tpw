import pygetwindow as gw
from PIL import ImageGrab
import pyautogui

# 假设我们要截取名为"Notepad"的窗口
#notepad = gw.getWindowsWithTitle('无标题 - 记事本')[0]  # 获取窗口对象
notepad = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
# 确保窗口已经被发现
if notepad:
    notepad.activate()  # 激活窗口
    #notepad.maximize()  # 最大化窗口

    # 获取窗口的区域
    left, top, right, bottom = notepad.left, notepad.top, notepad.right, notepad.bottom
    width, height = right - left, bottom - top

    # 截取屏幕区域的图像
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

    screenshot.show()  # 显示截图
    screenshot.save('notepad_screenshot.png')  # 保存截图到文件
else:
    print("未找到窗口")