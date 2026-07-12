import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
import win32api
import win32gui, win32ui
import win32con
import time
import os
import mss
import re
from base64 import b64encode
from matplotlib.path import Path
from pygetwindow import Win32Window
from circleHandle import getCircle
from log import Log
from queue import Queue
cardQueue = Queue(30)
logger = Log().get_log()
lock = threading.RLock()
lock3 = threading.RLock()
lock4 = threading.RLock()
path = os.path.dirname(os.path.realpath(__file__))
pool = ThreadPoolExecutor(max_workers=15)
from WxAuToTool import WxAuToTool
import threading
import win32com.client as win32
import pythoncom

import re

import random

def pictureImg(hwnd: int, x: int, y: int, x1: int, y1: int,back:int):
    if back != 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
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
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        cv2.imwrite("C:/test_game/"+str(hwnd)+"hzend.png", cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR))
    elif back == 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
            with mss.mss() as sct:
                hwndWindow = Win32Window(hwnd)
                # 获取窗口的区域
                left, top, right, bottom = hwndWindow.left, hwndWindow.top, hwndWindow.right, hwndWindow.bottom
                box = {"top": top + y, "left": left + x, "width": w, "height": h}

                image_sct = sct.grab(box)
                im_opencv = np.array(image_sct)
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        cv2.imwrite("C:/test_game/"+str(hwnd)+"hzend.png", cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR))

pictureImg(135770,39,63,979,593,1)
# whos = "当前空车.:.微信喊话内容dsfs|sdfsfsdf".split(".:.")
#
# print(whos[0])


# def extract_numbers(s):
#     try:
#         numbers = re.findall(r'\d+', s)  # \d+ 匹配一个或多个数字
#         numbers = [int(num) for num in numbers][1]
#         if numbers > 999:
#             return numbers
#     except Exception as e:
#         return ""
#
#
# # 使用示例
# s = "1号房间 1234 "
# numbers = extract_numbers(s)
# print(numbers)  # 输出: [123, 456]


# my_dict = {
#     "apple": 1,
#     "banana": 2,
#     "cherry": 3
# }
# result =""
# for key, value in my_dict.items():
#     childStr = str(key) + ":" + str(value)
#     result = result + "|" + childStr
#
# print(result[1:])






# def com_function():
#     outlook = win32.Dispatch('Outlook.Application')
#     # 其他COM操作
#
# # 创建线程前初始化COM
# win32.gencache.EnsureDispatch('Outlook.Application')
# def wxWorker(whos, hwnd):
#     pythoncom.CoInitialize()
#     outlook = win32.Dispatch('Outlook.Application')
#     wxAuToTool = WxAuToTool(0)
#     wxAuToTool.wxWinHwndReg(whos,hwnd)
#     wxAuToTool.wxAuToStart()
# wobj = [
#     '小毛毛鱼',
#     '文件传输助手'
# ]
# #wxWorker(wobj,66832)
# wxT = threading.Thread(target=wxWorker, args=(wobj, 66832))
# wxT.start()
#
# pythoncom.CoUninitialize()


