import os
import sys
import numpy as np
import cv2
import win32gui, win32ui
import win32con
from matp_api import OcrAPI
import time
import re


# x = 496
#     y = 82
#     x1 = 546
#     y1 = 100
# 506,83,533,99
# 506,83,534,99  100以上
# 511,83,530,98 100-10
# 494,83,546,99
# 496,82,545,101
#杯子 148,93,222,117  148,91,222,119
# 聊天： 793,233,942,290

#杯子 148,91,222,119
#512,84,528,99 关卡1-9
#494,82,547,99 关卡 10-310
def getImage():
    x = 148
    y = 91
    x1 = 222
    y1 = 119
    w = x1 - x
    h = y1 - y
    hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
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
    img = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
    cv2.imshow("img", img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    retval, buffer = cv2.imencode('.png', img)
    return buffer


def filter_numbers(s):
    return re.findall(r'\d+', s)

def is_number(value):
    pattern = r'^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$'
    return bool(re.match(pattern, str(value)))

def getOcrTxt(res: dict,oldNumbers:int):
    if res["code"] == 100:
        score = 0
        levels = 0
        numbers = 0
        for line in res["data"]:
            score = round(line['score'], 2)
            levels = line['text']
            print(f"-置信度：{score}，文本：{levels}")
            if score >= 0.75:
                numbers = filter_numbers(levels)
                if(numbers.__len__()<=0):
                    break
                numbers = int(numbers[0])
                if is_number(numbers):
                    if oldNumbers == 0:
                        if numbers > 0:
                            oldNumbers = numbers
                            print(f"当前关卡为：{oldNumbers}")
                            return numbers
                    elif(numbers > 0 and numbers >= oldNumbers and numbers <= (oldNumbers + 5)):
                        oldNumbers = numbers
                        print(f"当前关卡为：{oldNumbers}")
                        return numbers
    elif res["code"] == 100:
        print("图片中未识别出文字。")
    else:
        print(f"图片识别失败。错误码：{res['code']}，错误信息：{res['data']}")


ocrPath = r"./matp.exe"
if not os.path.exists(ocrPath):
    print(f"未在以下路径找到引擎！\n{ocrPath}")
    sys.exit()
ocr = OcrAPI(ocrPath)

# 路径识图
print("OCR初始化完毕，开始路径识图。")
oldnum = 0;
for i in range(1000000):
    time.sleep(1)
    imageBytes = getImage()
    res = ocr.runBytes(imageBytes)

    newNum=getOcrTxt(res,oldnum)
    if(newNum):
        oldnum = newNum
    else:
        print(f"不是数字：{newNum}")
