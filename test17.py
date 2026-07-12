import mss
import pygetwindow as gw
from PIL import ImageGrab
import cv2 as cv
import numpy as np
import win32gui, win32ui
from PIL import Image
import pyautogui

# 假设我们要截取名为"Notepad"的窗口
from pygetwindow import Win32Window

#hwid = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
#notepada = gw.getWindowsWithTitle('塔防精灵')[0]  # 获取窗口对象
#notepad=  Win32Window(hwid)
notepad = gw.getWindowsWithTitle('无标题 - 记事本')[0]  # 获取窗口对象
if notepad:
    #notepad.activate()  # 激活窗口

    # 获取窗口的区域
    left, top, right, bottom = notepad.left, notepad.top, notepad.right, notepad.bottom
    width, height = right - left, bottom - top

    #COLOR_BGR2GRAY COLOR_BGRA2BGR COLOR_BGR2HSV
    # 设置截图区域的坐标和尺寸
    with mss.mss() as sct:
        #400,517,640,608
        #  w = x1 - x
        #h = y1 - y
        # x y

        x = 400
        y = 517
        x1 = 640
        y1 = 608
        w = x1 - x
        h = y1 - y
        print(top)
        print(left)
        print(width)
        print(height)

        box ={"top":top,"left":left,"width":width,"height":height}
        #box ={"top":top+y,"left":left+x,"width":w,"height":h}

        image_sct = sct.grab(box)
        image_array = np.array(image_sct)
        image_array = cv.convertScaleAbs(image_array)
        #image_cv = cv.cvtColor(image_array, cv.COLOR_BGR2GRAY)
        #cv.imshow("img_thr", image_cv)

        #cv.waitKey(0)
        #cv.destroyAllWindows()
        #mss.tools.to_png(im.rgb,im.size,output="11111111111.png")

        #cv.imshow("img_thr", img_thr)
        #cv.imshow("dst", dst)
image_cv = cv.cvtColor(image_array, cv.COLOR_BGR2GRAY)
cv.imshow("img_thr", image_cv)

cv.waitKey(0)
cv.destroyAllWindows()