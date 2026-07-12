import os
import random
from shutil import move
import time
import win32con
import win32gui,win32ui
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox
)
import sys

class Picture2(QMainWindow):
    imgUrls=[]
    cardName = []

    def __init__(self, parent=None):
        super().__init__(parent)

        #self.view_images("",2,"ss")

    def view_images(self,imgUrl:str,tag,name:str):
        self.imgUrls.append(imgUrl)
        self.cardName.append(name)
        #imgUrl = imgUrl.replace("\\", "\\\\")
        #print(f"imgUrl:{imgUrl}")
        #print(f"tag:{tag}")
        #print(f"name:{name}")
        scene = QtWidgets.QGraphicsScene()  # 加入 QGraphicsScene
        img = QtGui.QPixmap(imgUrl)
        scene.addPixmap(img)  # 將图片加入 scene
        if tag == 1:
            self.ui.grview.setScene(scene)
            self.ui.textEdit.setText(name)
        elif tag == 2:
            self.ui.grview_2.setScene(scene)
            self.ui.textEdit_2.setText(name)
        elif tag == 3:
            self.ui.grview_3.setScene(scene)
            self.ui.textEdit_3.setText(name)



    #识别
    def identify(self):
        self.imgUrls = []
        self.cardName = []
        hwnd = 5977296
        i = 3
        while i > 0:
            w = 49
            h = 74
            w1 = 410
            h1 = 526
            if i == 0:
                #410, 526, 459, 600  49,74
                w = 49
                h = 74
                w1 = 410
                h1 = 526
            elif  i == 1:
                # 495,526,544,599,宽高(49,73)
                w = 49
                h = 73
                w1 = 495
                h1 = 526
            elif  i == 2:
                #580,527,629,598,宽高(49,71)
                w = 49
                h = 71
                w1 = 580
                h1 = 527
            hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
            saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
            saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
            saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap
            saveDC.BitBlt((0, 0), (w, h), mfcDC, (w1, h1), win32con.SRCCOPY)  # 截取从左上角（0，0）长宽为（w，h）的图片
            signedIntsArray = saveBitMap.GetBitmapBits(True)
            im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
            im_opencv.shape = (h, w, 4)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            sourceimg = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("sourceimg", sourceimg)
            #cv2.waitKey()

            path = os.path.realpath(__file__)
            fileName = os.path.dirname(path) + "\手牌"
            listdirs = os.listdir(fileName)
            bool = 1
            for childFile in listdirs:
                #print(childFile)
                fileName = os.path.dirname(path) + "\手牌\\"+childFile
                if os.path.isdir(fileName)==False:
                    print(f"文件夹不存在：{fileName}")
                    continue
                listdirs = os.listdir(fileName)
                for card in listdirs:
                    cardGray = cv2.imdecode(np.fromfile(fileName + "\\" + card, dtype=np.uint8), 0)
                    #print(f"cardGray:{cardGray}")
                    match = cv2.matchTemplate(cardGray,sourceimg, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match > 0.9)
                    if len(locathions[0]) == 0:
                        #print("没识别到，生成截图")
                        pass
                    else:
                        print(f"识别到图片：{childFile}")
                        bool = 0
                        self.view_images(fileName + "\\" + card,i,childFile)
                        break



            if bool == 1:
                print("开始生成截图")
                # 将当前时间转化为时间戳
                timestamp = int(time.time())
                random_number = str(random.randint(0, 10000000))
                sourceImg = str(timestamp) + random_number + ".tif"
                # 打印时间戳
                print(f"当前时间戳为{timestamp}")
                path = os.path.realpath(__file__)
                pathout = os.path.dirname(path) + "\临时卡牌\\" + sourceImg
                cv2.imencode('.tif', sourceimg)[1].tofile(pathout)
                # img1 = cv2.imdecode(np.fromfile("temimg.tif", dtype=np.uint8), 0)
                self.view_images(pathout, i, "未识别")
            i -=1
    def saveImg(self):
        count = 0
        while count < 3:
            imgUrl = self.imgUrls[count]
            if count == 0:
                name = self.ui.textEdit.toPlainText()
            elif count == 1:
                name = self.ui.textEdit_2.toPlainText()
            elif count == 2:
                name = self.ui.textEdit_3.toPlainText()

            if "临时卡牌" in imgUrl:
                path = os.path.realpath(__file__)
                pathout = os.path.dirname(path) + "\手牌\\" + name + "\\" + imgUrl.split("\\")[-1]
                move(imgUrl, pathout)
                print(f"{name}保存文件成功：{imgUrl}")
                '''path = os.path.realpath(__file__)
                pathout =  os.path.dirname(path) + "\手牌\\"+name+"\\"+imgUrl.split("\\")[-1]
                img = cv2.imdecode(np.fromfile(imgUrl, dtype=np.uint8),-1)
                cv2.imshow("img", img)
                cv2.waitKey()
                cv2.imencode('.jpg', img)[1].tofile(pathout)
                print(f"{name}保存文件成功：{imgUrl}")
                os.remove(imgUrl)'''
            count +=1

if __name__ == '__main__':


    app = QtWidgets.QApplication(sys.argv)
    # 创建一个widget组件基础类
    windows = QtWidgets.QWidget()
    # 设置widget组件的大小(w,h)
    windows.resize(500, 500)
    # 设置widget组件的位置(x,y)
    windows.move(100, 100)
    """
    #设置widget组件的位置居中
    qr = windows.frameGeometry()
    cp = QtWidgets.QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    windows.move(qr.topLeft())
    """
    # 等同于 w.resize(500,500)和w.move(100,100)两句结合,(x,y,w,h)
    # windows.setGeometry(100,100,500,500)
    # show()方法在屏幕上显示出widget组件

    QMessageBox.information(windows, "提示", f"登录失败:", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)

    windows.show()



    # 循环执行窗口触发事件，结束后不留垃圾的退出，不添加的话新建的widget组件就会一闪而过
    sys.exit(app.exec_())




