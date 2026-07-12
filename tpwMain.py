import ctypes
import os
import random
from shutil import move,rmtree
import time
import win32con
import win32gui,win32ui
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui
from adodbapi.adodbapi import Dispatch
import DmTool
from fightThread import FightThread
from log import Log

from ui.tpwMainUI import Ui_MainWindow
from PyQt5.QtWidgets import (
    QMainWindow,QMessageBox
)
import sys
from webServer import webAppServerStart
import threading
import yanzheng

logger = Log().get_log()
class TpwMain(QMainWindow):
    imgUrls= {}
    hwnd = 0
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.identify)
        self.ui.pushButton_2.clicked.connect(self.saveImg)
        self.ui.pushButton_3.clicked.connect(self.webServerStart)
        self.ui.pushButton_4.clicked.connect(self.gameFlash)
        self.ui.pushButton_5.clicked.connect(self.getGameHwnd)
        self.ui.pushButton_6.clicked.connect(self.register)
        self.ui.pushButton_8.clicked.connect(self.stop)
        #脚本启动
        self.ui.pushButton_7.clicked.connect(self.start)
        self.setWindowTitle("躺平王")


        #self.view_images("",2,"ss")
    def stop(self):
        try:
            self.fight.terminate()
            self.ui.pushButton_7.setEnabled(True)
            self.ui.pushButton_7.setText("启动")
            self.ui.pushButton_8.setEnabled(False)
            self.ui.pushButton_8.setText("已停止")
            logger.info("脚本停止")
        except Exception as e:
            logger.error(f"脚本停止发送异常:{str(e)}")
    # 脚本启动
    def start(self):
        logger.info("脚本启动开始")
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_7.setText("已启动")
        #绑定游戏
        '''resBind = self.bindGame()
        if resBind == 0:
            QMessageBox.information(self, "提示", "游戏启动失败，请打开游戏，游戏不能最小化", QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
            self.ui.pushButton_7.setEnabled(True)
            self.ui.pushButton_7.setText("启动")
            return'''
        self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
        self.ui.lineEdit_2.setText("小鹿|萨满|海妖|冰骑|死神|地精|斧客|绿弓|电法|骨弓")
        battleCard = self.ui.lineEdit_2.text()
        battleCard = battleCard.split("|")
        battleCard = list(filter(None, battleCard))
        self.battleCard = battleCard
        if len(battleCard) == 0 or len(battleCard) < 10:
            QMessageBox.information(self, "提示", "对战阵容数量不对", QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
            self.ui.pushButton_7.setEnabled(True)
            self.ui.pushButton_7.setText("启动")
        else:
            #self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
            if self.hwnd == 0:
                QMessageBox.information(self, "提示", "启动失败，请先打开游戏", QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)
                self.ui.pushButton_7.setEnabled(True)
                self.ui.pushButton_7.setText("启动")
            else:
                res = DmTool.FindStr(self.hwnd, "对战", 808, 533, 989, 600)
                if len(res) > 0:
                    self.ui.pushButton_8.setEnabled(True)
                    self.ui.pushButton_8.setText("停止")

                    self.fight = FightThread(self.hwnd,self.battleCard)
                    self.fight.daemon=True
                    self.fight.start()
                else:
                    QMessageBox.information(self, "提示", "游戏请回到主界面再启动", QMessageBox.StandardButton.Ok,
                                            QMessageBox.StandardButton.Ok)
                    self.ui.pushButton_7.setEnabled(True)
                    self.ui.pushButton_7.setText("启动")

    def pyqtSignalTest(self):
        print("6666666")
    def register(self):
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_6.setText("登录中。。。")
        self.ui.lineEdit.setText("7d4f3b11fb1e8994")
        lineEditVal = self.ui.lineEdit.text()

        res = -1
        if len(lineEditVal) > 0:
            yanzheng.selfObj=self
            res = yanzheng.register(lineEditVal)
        if res == 0:
            self.ui.label.hide()
            self.ui.lineEdit.hide()
            self.ui.groupBox.hide()
        else:
            QMessageBox.information(self, "提示", f"登录失败:{res}", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
        self.ui.pushButton_6.setEnabled(True)
        self.ui.pushButton_6.setText("登录")

    def webServerStart(self):
        print(f"os.getpid()qqqq:{os.getpid()}")
        islogin = yanzheng.isLogin()
        if islogin == 0:
            t1 = threading.Thread(target=webAppServerStart)
            t1.start()
            self.ui.pushButton_3.setEnabled(False)
            self.ui.pushButton_3.setText("已启动")
        else:
            QMessageBox.information(self, "提示", f"登录失败,请先登录", QMessageBox.StandardButton.Ok,QMessageBox.StandardButton.Ok)

    def gameFlash(self):
        if self.hwnd > 0:
            DmTool.leftClick(self.hwnd,722,572)
        else:
            QMessageBox.information(
                self, "消息", "请先获取游戏id", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)

    def getGameHwnd(self):
        self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
        # 获取窗口标题
        title = win32gui.GetWindowText(self.hwnd)
        print(f"窗口标题：{title} 句柄：{self.hwnd}")
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_5.setText(title+":"+str(self.hwnd))



    def view_images(self,imgUrl:str,tag,name:str):
        self.imgUrls.append(imgUrl)
        #imgUrl = imgUrl.replace("\\", "\\\\")
        #print(f"imgUrl:{imgUrl}")
        #print(f"tag:{tag}")
        #print(f"name:{name}")
        scene = QtWidgets.QGraphicsScene()  # 加入 QGraphicsScene
        img = QtGui.QPixmap(imgUrl)
        scene.addPixmap(img)  # 將图片加入 scene
        if tag == 0:
            self.ui.grview.setScene(scene)
            self.ui.textEdit.setText(name)
        elif tag == 1:
            self.ui.grview_2.setScene(scene)
            self.ui.textEdit_2.setText(name)
        elif tag == 2:
            self.ui.grview_3.setScene(scene)
            self.ui.textEdit_3.setText(name)

    #识别
    def identify(self):
        if self.hwnd == 0:
            QMessageBox.information(
                self, "消息", "请先获取游戏id", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        self.imgUrls = []
        hwnd = self.hwnd
        path = os.path.realpath(__file__)
        rmtree(os.path.dirname(path) + "\临时卡牌")
        os.makedirs(os.path.dirname(path) + "\临时卡牌")
        i = 0
        while i < 3:
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
            elif i == 1:
                # 495,526,544,599,宽高(49,73)
                w = 49
                h = 73
                w1 = 495
                h1 = 526
            elif i == 2:
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


            fileName = os.path.dirname(path) + "\手牌"
            listdirs = os.listdir(fileName)
            bool = 1
            for childFile in listdirs:
                #print(childFile)
                fileName = os.path.dirname(path) + "\手牌\\"+childFile
                if os.path.isdir(fileName)==False:
                    #print(f"文件夹不存在：{fileName}")
                    continue
                listdirs = os.listdir(fileName)
                for card in listdirs:
                    cardGray = cv2.imdecode(np.fromfile(fileName + "\\" + card, dtype=np.uint8), 0)
                    #print(f"cardGray:{cardGray}")
                    match = cv2.matchTemplate(cardGray,sourceimg, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match > 0.8)
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

                pathout = os.path.dirname(path) + "\临时卡牌\\" + sourceImg
                cv2.imencode('.tif', sourceimg)[1].tofile(pathout)
                # img1 = cv2.imdecode(np.fromfile("temimg.tif", dtype=np.uint8), 0)
                self.view_images(pathout, i, "未识别")
            i +=1
    def saveImg(self):
       print("保存训练图")
       if self.hwnd == 0:
           QMessageBox.information(self, "消息", "请先获取游戏id", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
           return
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
               pathout = os.path.dirname(path) + "\手牌\\" + name
               if os.path.isdir(pathout) == False:
                   QMessageBox.information(
                       self, "消息", f"{name}:保存失败", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
                   count += 1
                   continue
               pathout = pathout + "\\" + imgUrl.split("\\")[-1]
               move(imgUrl, pathout)
               print(f"{name}保存文件成功：{imgUrl}")
               QMessageBox.information(
                   self, "消息", f"{name}:保存成功", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
               '''path = os.path.realpath(__file__)
               pathout =  os.path.dirname(path) + "\手牌\\"+name+"\\"+imgUrl.split("\\")[-1]
               img = cv2.imdecode(np.fromfile(imgUrl, dtype=np.uint8),-1)
               cv2.imshow("img", img)
               cv2.waitKey()
               cv2.imencode('.jpg', img)[1].tofile(pathout)
               print(f"{name}保存文件成功：{imgUrl}")
               os.remove(imgUrl)'''
           count += 1

    def bindGame(self):
        # 免注册op
        opdll = ctypes.windll.LoadLibrary("./\\other\\tools_64.dll")
        resultdll = opdll.setupW("./\\other\\op_x64.dll")
        if resultdll == 0:
            print("注册码op失败")
            return 0
        time.sleep(0.1)
        self.op = Dispatch("op.opsoft")
        # 绑定窗口
        self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
        print(f"游戏id:{self.hwnd}")
        time.sleep(0.1)
        r = self.op.BindWindow(self.hwnd, "gdi", "normal", "normal", 0)
        time.sleep(0.2)
        if r == 0:
            print("绑定窗口失败");
            return 0
        else:
            print("绑定窗口成功！")
            return 1
            op_ret = self.op.Capture(85,50,976,434, "测试绑定.bmp")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = TpwMain()
    win.show()
    app.exit(app.exec())




