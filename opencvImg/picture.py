import os
import random
from shutil import move
import time
import win32con
import win32gui,win32ui
import cv2
import numpy as np
import img3
import img5
import img7
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox
)
import sys



def getGameHwnd():
    hwnd = 0
    try:
        hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
        print("游戏句柄：" + str(hwnd))
    except Exception as e:
        print(f"获取游戏id:{str(e)}")
    return  hwnd

#识别
def pictureImg(hwnd:int,x: int, y: int, x1: int, y1: int):
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
    sourceimg = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)


    timestamp = int(time.time())
    random_number = str(random.randint(0, 10000000))
    sourceImg = str(timestamp) + random_number + ".tif"
    path = os.path.realpath(__file__)
    pathout = os.path.dirname(path) + "\sourceImg\\" + sourceImg
    cv2.imencode('.tif', sourceimg)[1].tofile(pathout)
    # img1 = cv2.imdecode(np.fromfile("temimg.tif", dtype=np.uint8), 0)

def 截图():
    hwnd = getGameHwnd()
    for i in range(10000):
        time.sleep(0.2)
        print("11111")
        pictureImg(hwnd, 385, 511, 651, 615)

def 图片裁剪():
    #完美使用
    fileName3 = "I:\\tpw2\\手牌"
    listdirs3 = os.listdir(fileName3)

    for file3 in listdirs3:
        for ii in range(2):
            fileName4 = "I:\\tpw2\\手牌\\" + file3
            if ii == 1:
                fileName4 = "I:\\tpw2\\快速手牌\\" + file3
            listdirs4 = os.listdir(fileName4)
            for file4 in listdirs4:
                source = cv2.imdecode(np.fromfile(fileName4 + '\\' + file4, dtype=np.uint8), 0)
                imgsize = source.shape
                w = imgsize[0]
                h = imgsize[1]
                print(f"w:{w},h:{h}")
                if w == 86 and h == 64:
                    print(file4)
                    pathout = fileName4 + '\\' + file4
                    x = 8
                    y = 5
                    w = 61
                    h = 84


                    # 裁剪图像
                    cropped_image = source[x:h, y:w]

                    cv2.imencode('.tif', cropped_image)[1].tofile(pathout)
                    #cv2.imshow("cropped", source)
                    #cv2.waitKey(0)

def 识别():
    cardGray = cv2.imread("./tag/0604094415.527.tif", 0)

    #cardGray = img5.imgHandle("./1017104225.996.tif")
    #cv2.imshow("cardGray",cardGray)
    #cv2.waitKey()


    path = os.path.dirname(os.path.realpath(__file__))
    fileName = path + "\sourceImg"
    listdirs = os.listdir(fileName)
    start_time = time.time()

    fileName2 = path + "\\tag"
    fileName3 = "I:\\tpw2\\手牌"
    listdirs3 =os.listdir(fileName3)
    #listdirs2= os.listdir(fileName2)
    #res = img7.imgHandle("./tag/16940896636273952.tif", fileName + '\\' + "16987461343943658.tif")
   # return 1
    count = 0
    '''f
                        fileName4 = "I:\\tpw2\\手牌\\"+file3
                        listdirs4 = os.listdir(fileName4)
                        for file4 in listdirs4:
                            res = img7.imgHandle(fileName4 + '\\' + file4, fileName + '\\' + file)
                            if res == 1:
                                #cv2.imshow("source", source)
                                #cv2.imshow("cardGray", cardGray)
                                #cv2.waitKey()
                                #print("识别成功：" +file )
                                count +=1'''

    for file in listdirs:
        for file3 in listdirs3:
            for ii in range(2):
                fileName4 = "I:\\tpw2\\手牌\\" + file3
                if ii == 1:
                    fileName4 = "I:\\tpw2\\快速手牌\\" + file3
                listdirs4 = os.listdir(fileName4)
                for file4 in listdirs4:

                    source = cv2.imdecode(np.fromfile(fileName + '\\' + file, dtype=np.uint8), 0)
                    cardGray =cv2.imdecode(np.fromfile(fileName4 + '\\' + file4, dtype=np.uint8), 0)



                    match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match >= 0.85)

                    # res = img7.imgHandle(fileName2 + '\\' + file2, fileName + '\\' + file)
                    if len(locathions[0]) == 0:
                        # if res == 0:
                        pass
                        # print("未识别到")
                    else:
                        time.sleep(2)
                        cv2.imshow("cardGray", cardGray)
                        cv2.waitKey(3)
                        temData = list(zip(*locathions[::-1]))[0]
                        x = temData[0]
                        y = temData[1]
                        print("识别成功：" + file3)
                        cv2.putText(source, "@@", (x + 5, y + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 2)
                        cv2.imshow("source", source)
                        cv2.waitKey(3)
                        print("识别成功：" + file)
                        #res = img7.imgHandle(fileName4 + '\\' + file4, fileName + '\\' + file)
                        time.sleep(1)
                        cv2.destroyAllWindows()
                        # cv2.waitKey()
    return  1

    for file in listdirs:
        for file2 in listdirs2:
            source = cv2.imdecode(np.fromfile(fileName + '\\' + file, dtype=np.uint8), 0)
            cardGray = cv2.imread(fileName2 + '\\' + file2, 0)

            #source = img5.imgHandle(fileName + '\\' + file)
            #cv2.imshow("source", source)
            #cv2.waitKey()

            match = cv2.matchTemplate(source,cardGray,cv2.TM_CCOEFF_NORMED)
            locathions = np.where(match >= 0.95)

            #res = img7.imgHandle(fileName2 + '\\' + file2, fileName + '\\' + file)
            if len(locathions[0]) == 0:
            #if res == 0:
                pass
                #print("未识别到")
            else:

                temData = list(zip(*locathions[::-1]))[0]
                x = temData[0]
                y = temData[1]
                cv2.putText(source, '@@@', (x+5, y+20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 2)
                cv2.imshow("source", source)
                #cv2.imshow("cardGray", cardGray)
                cv2.waitKey()
                print("识别成功：" +file )
                '''for file3 in listdirs3:
                    fileName4 = "I:\\tpw2\\手牌\\"+file3
                    listdirs4 = os.listdir(fileName4)
                    for file4 in listdirs4:
                        res = img7.imgHandle(fileName4 + '\\' + file4, fileName + '\\' + file)
                        if res == 1:
                            #cv2.imshow("source", source)
                            #cv2.imshow("cardGray", cardGray)
                            #cv2.waitKey()
                            #print("识别成功：" +file )
                            count +=1'''

                        #cv2.waitKey()
    print("匹配的个数："+str(count))
    end_time = time.time()
    print("FindPic程序运行时间：%.2f秒" % (end_time - start_time))

图片裁剪()









