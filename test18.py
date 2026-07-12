import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
import win32api
import win32gui, win32ui
import win32con
import os
from matplotlibes.matp_api import OcrAPI
import DmTool

#hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "Chrome Legacy Window")
hwnd = win32gui.FindWindow("Chrome_RenderWidgetHostHWND", "Chrome Legacy Window")
def getimg(x,y,x1,y1):
    # x = 18
    # y = 199
    # x1 = 167
    # y1 = 279
    w = x1 - x
    h = y1 - y

    hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
    saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
    saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)  # 截取从左上角（0，0）长宽为（w，h）的图片
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
    im_opencv.shape = (h, w, 4)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    img = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR)
    return img

str="792,207,1032,528"
zb = str.split(",")
x = int(zb[0])
y = int(zb[1])
x1 = int(zb[2])
y1 = int(zb[3])
img = getimg(x,y,x1,y1)







cv2.imshow("img", img)

cv2.waitKey(0)
cv2.destroyAllWindows()






# ocrPath = r"./matplotlibes/matp.exe"
# ocr = OcrAPI(ocrPath)
# print(ocr.getTest())
# res = DmTool.FindStr(hwnd, "广告", x, y, x1, y1,0,ocr)
# print(res)
# res = res.split("|")
# x = res[0]+20
# y = res[1]-20
# x1 = x+60
# y1 = y+30
#
# img = getimg(x,y,x1,y1)
# #cv2.rectangle(img, (0, 0), (50, 50), (255, 0, 0), 3)
#
# cv2.imshow('Detected', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()