import json
import os
import time
import win32api
import win32con
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QScreen
from Plugin import shareData

import numpy as np
import DmTool
# 游戏线程
class GameThread(QThread):
    wnd: int = 0
    interval: float = 0.0
    uiSlot = pyqtSignal(str)
    screen: QScreen
    bStart: bool = False
    name = ""

    def __init__(self, screen, wnd, callback, interval=0.05, name="游戏线程"):
        super().__init__()
        self.wnd = wnd
        self.interval = interval
        self.screen = screen
        self.callback = callback

    def run(self) -> None:
        print("线程开始" + self.name)
        while self.bStart:
            print("开始识别")

            cards = ["小鹿", "萨满", "海妖", "冰骑", "死神", "地精", "斧客", "绿弓", "电法", "骨弓"]
            reslist = DmTool.FindPicS(self.wnd,cards,396,513,644,612)
            print("查询结果为：")
            print(reslist)

            if len(reslist) > 0:
                print("进入条件")
                getCard = reslist[0].split(",")
                print(f"getCard：{getCard}")
                self.clickLAt(self.wnd, int(getCard[1]), int(getCard[2]))



                time.sleep(0.5)
                count = 0
                while count < 5:
                    resultstr = DmTool.FindPic(self.wnd, getCard[0], 396, 513, 644, 612)
                    if len(resultstr) != 0:
                        print("继续点英雄")
                        self.clickLAt(self.wnd, int(getCard[1]), int(getCard[2]))
                        count += 1
                    else:
                        print("刷新")
                        self.clickLAt(self.wnd, 722, 579)
                        print(f"上英雄了结束循环：{count}")
                        break
                    time.sleep(0.3)
                    print(f"判断英雄是否上战车：{count}")

            extendBool = self.extend()
            if extendBool == 1:
                print("金币不足")
            else:
                print("扩建")
                self.clickLAt(self.wnd,320, 576)




            '''print("开始识别")
            resultYolo: list = shareData.plugin.detectRectYoloObject(self.wnd, "悟空",383,507,640,640,0.6)

            # 识别到返回坐标list xywh
            if len(resultYolo) >= 4:
                pass
                #print("识别yolo目标附近文字")
                #resultocr = shareData.plugin.detectRectText(self.wnd, resultYolo[0] - 50, resultYolo[1] - 50,resultYolo[2] + 25, resultYolo[3] + 150)
                #print(f"识别yolo目标附近文字结果为= {resultocr}")
            else:
               #resultocr = shareData.plugin.detectText(self.wnd)
               pass
            #if self.callback:
                #self.callback(f"yolo = {resultYolo}")
                #self.callback(f"ocr = {resultocr}")'''



            '''self.ocrClick(self.wnd, "对战", 846, 538, 953, 592)
            self.ocrClick(self.wnd, "快速匹配", 649, 509, 753, 543)
            self.ocrClick(self.wnd, "确定", 617,448,689,482)'''

            time.sleep(1)
            print("线程停止" + self.name)

    def LogUI(self, str):
        self.uiSlot.emit(str)

    # 刷新
    def flash(self):
        result = DmTool.findColor(self.wnd, 0, 0, 0, (int)(255 * 0.99), 255, (int)(255 * 0.64), 719, 594, 746, 614)
        return result

    # 扩建
    def extend(self):
        result = DmTool.findColor(self.wnd, 0, 0, 0, (int)(255 * 0.99), 255, (int)(255 * 0.64), 313, 588, 339, 612)
        return result

    # --点击方法--
    def clickLAt(self, wnd: int, x: int, y: int):
        # 模拟鼠标指针， 传送到指定坐标
        long_position = win32api.MAKELONG(x, y)
        # 模拟鼠标按下
        win32api.SendMessage(wnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        time.sleep(0.05)
        # 模拟鼠标抬起
        win32api.SendMessage(wnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
    def clickRAt(self, wnd: int, x: int, y: int):
        # 模拟鼠标指针， 传送到指定坐标
        long_position = win32api.MAKELONG(x, y)
        # 模拟鼠标按下
        win32api.SendMessage(wnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, long_position)
        time.sleep(0.05)
        # 模拟鼠标抬起
        win32api.SendMessage(wnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, long_position)

    def FindStr(self, wnd: int, strs:str,x: int, y: int, x1: int, y1: int):
        resultStr=shareData.plugin.detectRectText(wnd, x, y, x1-x, y1-y)
        if len(resultStr) < 3:
            return 0
        else:
            if strs in resultStr:
                jsonObj = json.loads(resultStr)
                jsonObj[strs][0] = x + jsonObj[strs][0]
                jsonObj[strs][1] = y + jsonObj[strs][1]
                return jsonObj[strs]
            else:
                return 0

    def ocrClick(self, wnd: int, strs: str, x: int, y: int, x1: int, y1: int):
        active = True
        while active:
            resultstr = self.FindStr(wnd, strs, x, y, x1, y1)
            if resultstr != 0:
                self.clickLAt(wnd, resultstr[0], resultstr[1])
                active = False


        '''img1=cv2.imread("df.jpg")
        img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        template=cv2.imread("AAAA.jpg")
        templategray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img1gray,templategray,cv2.TM_CCOEFF_NORMED)
        print(f"result:{result}")
        locathions = np.where(result > 0.9)
        print(f"locathions:{locathions}")
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
        print(f"最终结果：{min_loc}")
        #pi = str(min_loc).split(",")
        x = min_loc[0]+393
        y = min_loc[1]+510
        print(f"最终结果x：{x}") #585
        print(f"最终结果Y：{y}") # 542'''



    ''' # 读取原始图片
        img = cv2.imread('df3_x.bmp')
        # BGR -> RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 读取模板图片
        template = cv2.imread('AAAA.bmp')
        # BGR -> RGB
        template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

        # 显示图片
        plt.figure(figsize=(20, 20))
        plt.subplot(221), plt.imshow(template)
        plt.title('Template Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(img)
        plt.title('Origin Image'), plt.xticks([]), plt.yticks([])

        # 获取模板图片的高和宽
        th, tw = template.shape[0], template.shape[1]
        # rv是由每个位置的比较结果组合所构成的一个结果集，类型是单通道 32 位浮点型。
        rv = cv2.matchTemplate(img, template, cv2.TM_SQDIFF)
        # 查找最值（极值）与最值所在的位置
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(rv)
        # 左上角位置坐标
        topLeft = minLoc
        # 右下角角位置坐标
        bottomRight = (topLeft[0] + tw, topLeft[1] + th)
        # 绘制矩形
        cv2.rectangle(img, topLeft, bottomRight, (255, 255, 255), 5)
        # 显示图片
        plt.subplot(223), plt.imshow(rv)
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(img)
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.show()'''

    ''' # 显示图片
        plt.figure(figsize=(20, 20))
        plt.subplot(221), plt.imshow(source, cmap='gray')
        plt.title('Template Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(222), plt.imshow(target, cmap='gray')
        plt.title('Origin Image'), plt.xticks([]), plt.yticks([])

        # 获取模板图片的高和宽
        th, tw = source.shape[::]
        # rv是由每个位置的比较结果组合所构成的一个结果集，类型是单通道 32 位浮点型。
        rv = cv2.matchTemplate(target, source, cv2.TM_SQDIFF)
        # 查找最值（极值）与最值所在的位置
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(rv)
        # 左上角位置坐标
        topLeft = minLoc
        # 右下角位置坐标
        bottomRight = (topLeft[0] + tw, topLeft[1] + th)
        # 绘制矩形
        cv2.rectangle(target, topLeft, bottomRight, 255, 5)
        # 显示图片
        plt.subplot(223), plt.imshow(rv, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(224), plt.imshow(target, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.show()'''











