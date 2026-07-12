import json
import os
import threading
import time
from re import findall

import cv2
import numpy as np
import win32con
import win32gui
import win32ui
from Plugin import shareData
lock = threading.RLock()
class pyOcr:
    def Window_Img(self,hwnd: int, x: int, y: int, x1: int, y1: int, types=1):

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

        if types == 1:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
        else:
            '''cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
            #my_bytes = np.array(cv2.imencode('.jpg', im_opencv)[1]).tobytes()
            cv2.imwrite('messigray.png', im_opencv)'''
            return cv2.cvtColor(im_opencv, cv2.COLOR_RGBA2RGB)

    def __int__(self):

        print("初始化完成")

    def findOcr(self):
        for i in range(10):
            result = self.getOcr(2634150,144,87,217,123,0)
            print(f"识别结果：{result}")
            time.sleep(5)
            print("等待5秒再次执行")



    def getOcr(self,hwnd: int, x: int, y: int, x1: int, y1: int, tag: int):
        start_time = time.time()
        result = ""
        try:
            lock.acquire()
            resultStr = shareData.plugin.detectRectText(hwnd, x, y, x1 - x, y1 - y)
            lock.release()
            end_time = time.time()
            print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))
            if len(resultStr) < 3:
                return ""
            else:
                result = ""
                jsonObj = json.loads(resultStr)
                for key in jsonObj:
                    result = key
                    break
                if tag == 1 and len(result) > 0:
                    pattern = r'\d+'
                    result = findall(pattern, result)[0]
                return result
        except Exception as e:
            print(f"识别getOcr出错:{str(e)}")
            return result


if __name__ == '__main__':
    ocr = pyOcr()
    ocr.__int__()
    ocr.findOcr()
