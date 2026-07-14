import sys
import os
from types import ModuleType

# ===== 修复 certifi 证书路径问题（Nuitka 打包兼容） =====
# 错误分析：旧代码 certifi.where() 返回 ""（空字符串），
# 新版 requests(>=2.32) 在 adapters.py:81 导入时预加载 SSL 上下文，
# 调用 load_verify_locations("")，Windows OpenSSL 拒绝空路径 → OSError: [Errno 22]
# 修复方法：返回 cacert.pem 的真实路径，而不是空字符串

if getattr(sys, 'frozen', False):
    # Nuitka 打包后运行：cacert.pem 位于 exe 同级的 certifi 目录下
    _certifi_base = os.path.dirname(sys.executable)
else:
    # 源码直接运行
    _certifi_base = os.path.dirname(os.path.abspath(__file__))

_CERT_PATH = os.path.join(_certifi_base, 'certifi', 'cacert.pem')

# 伪造 certifi 模块，where() 必须返回有效的证书文件路径
fake_certifi = ModuleType("certifi")
fake_certifi.where = lambda p=_CERT_PATH: p

fake_certifi_core = ModuleType("certifi.core")
fake_certifi_core.where = lambda p=_CERT_PATH: p
fake_certifi.core = fake_certifi_core

sys.modules["certifi"] = fake_certifi
sys.modules["certifi.core"] = fake_certifi_core

# 同时设置环境变量（作为 urllib3 的后备读取路径）
os.environ["SSL_CERT_FILE"] = _CERT_PATH
os.environ["REQUESTS_CA_BUNDLE"] = _CERT_PATH


import random
import subprocess
import shutil
from multiprocessing import Process
from shutil import move,rmtree
import time
import ctypes
import win32gui,win32ui
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QIcon, QMovie
import requests
from PyQt5.QtGui import QDesktopServices
import DmTool
import mss
from killPid import clear
from pygetwindow import Win32Window
from ui.tpwWebMainUI import Ui_MainWindow
from PyQt5.QtWidgets import (
    QMainWindow,QMessageBox
)
from webServer import webAppServerStart
import loginCheck
from log import Log

# ── 增量更新系统 ──
from incremental_update.gui_updater import UpdateDialog

logger = Log().get_log()
class TpwMain(QMainWindow):


    imgUrls= {}
    hwnd = 0
    # 定义一个信号
    sendmsg = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.isLogin = "0"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.identify)
        self.ui.pushButton_2.clicked.connect(self.saveImg)
        self.ui.pushButton_3.clicked.connect(self.webServerStart)
        self.ui.pushButton_9.clicked.connect(self.webServerStop)
        self.ui.pushButton_4.clicked.connect(self.gameFlash)
        self.ui.pushButton_5.clicked.connect(self.getGameHwnd)
        self.ui.pushButton_6.clicked.connect(self.register)
        self.ui.pushButton_7.clicked.connect(self.incremental_update)
        self.ui.pushButton_8.clicked.connect(self.gameClear)
        self.ui.pushButton_10.clicked.connect(self.openUrl)
        self.ui.pushButton_11.clicked.connect(self.openUrl)

        self.setWindowTitle("躺平王服务端")
        self.sendmsg.connect(self.fileCopy)
        self.info()
    def openUrl(self):
        QDesktopServices.openUrl(QUrl("https://www.yuque.com/lufei-ou5am/ak0ekx/ku2fdtwzag2lb5xf?singleDoc#"))

    def closeEvent(self, event):
        result = QMessageBox.question(self, "提示", f"您确定要退出服务端吗？", QMessageBox.StandardButton.Ok,
                                      QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Ok:
            #yanzheng.退出登录()
            self.killTPW();
        else:
            event.ignore()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    def killTPW(self):
        # if not self.is_admin():
        #     # 请求管理员权限
        #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
        #     #sys.exit()

        process_name = "躺平王服务端.exe"  # 注意检查名称是否包含空格或特殊符号
        matp_name = "matp.exe"  # 注意检查名称是否包含空格或特殊符号

        try:
            logger.info(f"{matp_name}开始命令执行成功")
            subprocess.run(
                ["taskkill", "/F", "/IM", matp_name],
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="gbk"  # Windows 中文系统默认编码为 GBK
            )
            logger.info(f"{matp_name}命令执行成功")
        except subprocess.CalledProcessError as e:
            # 使用 GBK 编码解码错误信息
            error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode("gbk", errors="replace")
            logger.info(f"{matp_name}命令执行失败：{error_msg}")
            logger.info(f"{matp_name}详细原因：可能是进程不存在，或没有权限终止进程")
        except Exception as e:
            logger.info(f"{matp_name}其他错误：{str(e)}")

        try:
            logger.info(f"{process_name}开始命令执行成功")
            subprocess.run(
                ["taskkill", "/F", "/IM", process_name],
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="gbk"  # Windows 中文系统默认编码为 GBK
            )
            logger.info(f"{process_name}命令执行成功")
        except subprocess.CalledProcessError as e:
            # 使用 GBK 编码解码错误信息
            error_msg = e.stderr if isinstance(e.stderr, str) else e.stderr.decode("gbk", errors="replace")
            logger.info(f"{process_name}命令执行失败：{error_msg}")
            logger.info(f"{process_name}详细原因：可能是进程不存在，或没有权限终止进程")
        except Exception as e:
            logger.info(f"{process_name}其他错误：{str(e)}")

    def gameClear(self):
        result = QMessageBox.question(self, "提示", f"您确定要清理游戏缓存吗？", QMessageBox.StandardButton.Ok,
                                      QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Ok:
            cl=clear()
            cl.info()

    def incremental_update(self):
        """增量更新：仅下载变更文件，无需下载完整安装包"""
        # 更新服务器 URL —— 可通过 update_config.json 配置
        # 默认使用 GitHub + jsDelivr CDN 方案
        config_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "update_config.json"
        )
        server_url = "https://cdn.jsdelivr.net/gh/lvpingJava/tpw@v6.5.0.0"
        try:
            if os.path.exists(config_path):
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    server_url = config.get("server_url", server_url)
        except Exception:
            pass

        local_dir = os.path.dirname(os.path.realpath(__file__))

        dialog = UpdateDialog(server_url, local_dir, self)
        result = dialog.exec_()

        if dialog.was_update_successful():
            # 用户选择重启
            try:
                os.system('taskkill /f /im %s' % 'Runner.exe')
            except Exception:
                pass
            try:
                os.system('taskkill /f /im %s' % '躺平王客户端.exe')
            except Exception:
                pass
            try:
                os.system('taskkill /f /pid %s' % str(os.getpid()))
            except Exception:
                pass

    def udpate(self):
        result = QMessageBox.question(self, "提示", f"您确定要更新吗？ 辅助更新地址：https://cloud.189.cn/web/share?code=2ymiieaQRzum（密码：9lnu）", QMessageBox.StandardButton.Ok,
                                      QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Ok:
            QDesktopServices.openUrl(QUrl("https://cloud.189.cn/web/share?code=2ymiieaQRzum"))
            return
        else:
            return
        try:

            if self.oldVer.strip() == self.newVer.strip():
                QMessageBox.information(self, "提示", f"当前已经是最新版本，无需更新！", QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)

            else:
                result = QMessageBox.question(self, "提示", f"您确定要更新吗？", QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.No)
                if result == QMessageBox.StandardButton.Ok:
                    # 创建线程
                    self.updateTpw = UpdateTpwThread()
                    self.updateTpw.start()
                    time.sleep(0.5)
                    try:
                        os.system('taskkill /f /im %s' % 'Runner.exe')
                    except Exception as e:
                        pass

                    try:
                        os.system('taskkill /f /im %s' % '躺平王客户端.exe')
                    except Exception as e:
                        print(f"tpwWebMain.exe")

                    try:
                        os.system('taskkill /f /pid %s' % str(os.getpid()))
                    except Exception as e:
                        print(e)
                    time.sleep(0.5)
                    sys.exit(0)
        except Exception as e:
            logger.info(f"更新出错:{str(e)}")

    def info(self):
        try:

            isAdmin = ctypes.windll.shell32.IsUserAnAdmin()
            if isAdmin == True:
                # 以管理员身份运行的代码
                logger.info("管理员权限已获取")
            else:
                # 获取当前脚本的路径（处理路径中的空格问题）
                script = sys.argv[0]
                if " " in script:
                    script = f'"{script}"'  # 路径含空格时添加引号

                # 请求管理员权限并重新启动脚本
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, script, None, 0
                )
                sys.exit()  # 终止当前非管理员进程

            path = "C:\\test_game\\注册码.txt"
            if os.path.exists(path):
                f = open(path, encoding="utf-8")
                self.ui.lineEdit.setText(f.read(16))
                f.close()
        except Exception as e:
            logger.info(f"初始化失败:{str(e)}")

    def register(self):
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_6.setText("登录中......")
        lineEditVal = self.ui.lineEdit.text().strip()
        logger.info(f"aa:{lineEditVal}")
        try:
            res = [""]
            if len(lineEditVal) > 0:
                #yanzheng.selfObj = self
                res = loginCheck.getCheckResult(lineEditVal)
                logger.info(f"res[0]:{res[0]}")
                #res = 0
            if res[0] == 'OK':
                try:
                    getRegisterInfo = res[1]
                except Exception as e:
                    logger.info(f"getRegisterInfo出错:{str(e)}")
                    getRegisterInfo=["123","123"]
                self.isLogin = "1"
                # 更新判断
                # 打开文件
                localFile = open('./models/tpwVer.txt', 'r', encoding='ISO8859-1')
                # 读取文件内容
                localContent = localFile.read()
                # 关闭文件
                localFile.close()
                locallines = localContent.split("\n")
                if len(locallines) > 0:
                    localfirst_line = locallines[0]
                    self.oldVer = localfirst_line

                self.ui.label_5.setText("躺平王" + self.oldVer)
                self.ui.label_5.setAlignment(QtCore.Qt.AlignTrailing)
                self.ui.label_3.hide()
                self.ui.plainTextEdit.hide()

                # tpwVer 版本对比
                # Download_addres = 'http://47.101.48.90:8888/down/xFr6oM2JVYYo'
                # 把下载地址发送给requests模块
                # f = requests.get(Download_addres)
                # 下载文件
                remoteVersion = getRegisterInfo[0]
                remoteContent = ""
                for line in getRegisterInfo:
                    remoteContent = remoteContent + line + "\n"
                if len(remoteVersion) > 0:
                    self.newVer = remoteVersion
                if self.oldVer.strip() == remoteVersion.strip():
                    logger.info("版本匹配")
                else:
                    self.ui.plainTextEdit.show()
                    #self.ui.plainTextEdit.setPlainText("更新内容如下：")
                    self.ui.plainTextEdit.appendPlainText(remoteContent)
                    self.ui.label_3.show()
                    self.gif = QMovie('./models/new.gif')
                    self.ui.label_3.setMovie(self.gif)
                    self.gif.start()



                self.ui.label.hide()
                self.ui.lineEdit.hide()
                self.ui.groupBox.hide()
                path = "C:\\test_game"
                if not os.path.exists(path):
                    os.makedirs(path)
                    logger.info("Folder created")

                f = open(path+"\注册码.txt", "w")
                f.write(lineEditVal)
                f.close()
            else:
                QMessageBox.information(self, "提示", f"登录失败:{res[0]}", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            self.ui.pushButton_6.setEnabled(True)
            self.ui.pushButton_6.setText("登录")

            # 更新计划
            # Download_addres = 'http://47.101.48.90:8888/down/9MdkKvYcDSHJ'
            # 把下载地址发送给requests模块
            # f = requests.get(Download_addres)
            # 下载文件
            localFile = open('./models/update.txt', 'r', encoding='UTF-8')
            # 读取文件内容
            localContent = localFile.read()
            # f.close()
            self.ui.plainTextEdit_4.setPlainText(localContent)

        except Exception as e:
            logger.info(f"启动服务出错:{str(e)}")
    def fileCopy(self):
        logger.info("复制文件开始:")
        start_time = time.time()
        try:
            path = os.path.dirname(os.path.realpath(__file__))
            fileName = path + "\配置"

            user_path = os.path.expanduser('~') + "\AppData\Roaming\MyMacro\plugin"
            if not os.path.exists(user_path+"\\DMPJ.DLL"):
                shutil.copy(fileName+"\\DMPJ.DLL", user_path)
                logger.info("复制DMPJ.dll")
            if not os.path.exists(user_path +"\\DmReg.DLL"):
                shutil.copy(fileName+"\\DmReg.dll", user_path)
                logger.info("复制DmReg.dll")


            if os.path.isdir(fileName) == False:
                logger.info("配置文件夹不存在")
            else:
                listdirs = os.listdir(fileName)
                for file in listdirs:
                    try:
                        src_path = fileName + "\\" + file
                        dst_path = "C:\\test_game\\" + file
                        if os.path.exists(dst_path) and ".txt" not in file:
                            logger.info(f"文件存在返回：{dst_path}")
                            continue
                        else:
                            logger.info("复制文件："+file)
                            shutil.copy(src_path, dst_path)
                    except Exception as e:
                        logger.info(f"辅助配置文件错误:{str(e)},{file}")
        except Exception as e:
            logger.info(f"辅助配置文件错误:{str(e)}")
        end_time = time.time()
        logger.info("复制文件运行时间：%.2f秒" % (end_time - start_time))

    def webServerStart(self):
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_3.setText("已启动")
        self.ui.pushButton_9.setEnabled(True)
        self.ui.pushButton_9.setText("停止服务")
        try:
            logger.info("启动服务开始")
            islogin = self.isLogin

            if islogin == "1" :
                prot = self.ui.lineEdit_2.text().strip()
                if len(prot) > 0:
                    prot = int(prot)
                else:
                    prot = 5000
                f = open("C:\\test_game\\port.txt", "w")
                f.write(str(prot))
                #暂时不给时间提醒，给给默认时间：2108-01-08 17:58:51
                self.webAppServer = Process(target=webAppServerStart,args=("2108-01-08 17:58:51", prot))
                self.webAppServer.daemon = True
                self.webAppServer.start()
                logger.info(f"启动服务成功,端口为:{str(prot)}:" + islogin)
                self.sendmsg.emit()
            else:
                QMessageBox.information(self, "提示", f"登录失败,请先登录", QMessageBox.StandardButton.Ok,QMessageBox.StandardButton.Ok)
                logger.info(f"启动服务失败，请先登录")
                self.ui.pushButton_3.setEnabled(True)
                self.ui.pushButton_3.setText("启动服务")
                self.ui.pushButton_9.setEnabled(True)
                self.ui.pushButton_9.setText("停止服务")
        except Exception as e:
            logger.info(f"启动服务出错:{str(e)}")
            self.ui.pushButton_3.setEnabled(True)
            self.ui.pushButton_3.setText("启动服务")
            self.ui.pushButton_9.setEnabled(True)
            self.ui.pushButton_9.setText("停止服务")
        finally:
            pass

    def webServerStop(self):
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_3.setText("启动服务")
        self.ui.pushButton_9.setEnabled(False)
        self.ui.pushButton_9.setText("已停止")
        logger.info("开始停止服务")
        try:
            os.system('taskkill /f /im %s' % 'matp.exe')
            self.webAppServer.terminate()
            self.webAppServer.kill()
            logger.info("停止服务成功")
        except Exception as e:
            logger.info(f"停止服务出错:{str(e)}")
            self.ui.pushButton_3.setEnabled(True)
            self.ui.pushButton_3.setText("启动服务")
            self.ui.pushButton_9.setEnabled(True)
            self.ui.pushButton_9.setText("停止服务")
        finally:
            pass

    def webServerStopAll(self,msg:str):
        self.webServerStop()
        QMessageBox.information(self, "提示", f"辅助登录失败:{msg}", QMessageBox.StandardButton.Ok,
          QMessageBox.StandardButton.Ok)
    def gameFlash(self):
        if self.hwnd > 0:
            DmTool.leftClick(self.hwnd,722,572)
        else:
            QMessageBox.information(
                self, "消息", "请先获取游戏id", QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)

    def getGameHwnd(self):
        try:
            self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
            # 获取窗口标题
            title = win32gui.GetWindowText(self.hwnd)
            logger.info(f"窗口标题：{title} 句柄：{self.hwnd}")
            #self.ui.pushButton_5.setEnabled(False)
            self.ui.pushButton_5.setText(title+":"+str(self.hwnd))
        except Exception as e:
            logger.info(f"获取游戏id:{str(e)}")


    def view_images(self,imgUrl:str,tag,name:str):
        try:
            self.imgUrls.append(imgUrl)
            #imgUrl = imgUrl.replace("\\", "\\\\")
            #print(f"imgUrl:{imgUrl}")
            #print(f"tag:{tag}")
            #print(f"name:{name}")
            scene = QtWidgets.QGraphicsScene()  # 加入QGraphicsScene
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
        except Exception as e:
            logger.info(f"截图失败:{str(e)}")

    #识别
    def identify(self):
        logger.info("识别开始:")
        try:
            start_time = time.time()
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
                #底图
                if i == 0:
                    # 392,510,473,614,宽高(81,104)
                    w = 81
                    h = 104
                    w1 = 392
                    h1 = 510
                elif i == 1:
                    # 479,511,558,614,宽高(79,103)

                    w = 79
                    h = 103
                    w1 = 479
                    h1 = 511
                elif i == 2:
                    # 565,512,646,612,宽高(81,100)
                    w = 81
                    h = 100
                    w1 = 565
                    h1 = 512
                with mss.mss() as sct:
                    hwndWindow = Win32Window(hwnd)
                    # 获取窗口的区域
                    left, top, right, bottom = hwndWindow.left, hwndWindow.top, hwndWindow.right, hwndWindow.bottom
                    box = {"top": top + h1, "left": left + w1, "width": w, "height": h}

                    image_sct = sct.grab(box)
                    im_opencv = np.array(image_sct)
                imgs = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
                # cv2.imshow("sourceimg", sourceimg)
                # cv2.waitKey()


                fileName = os.path.dirname(path) + "\手牌"
                listdirs = os.listdir(fileName)
                bool = 1
                for childFile in listdirs:
                    #print(f"card:{childFile}")
                    #print(childFile)
                    fileName = os.path.dirname(path) + "\手牌\\"+childFile
                    if os.path.isdir(fileName)==False:
                        #print(f"文件夹不存在：{fileName}")
                        continue
                    listdirs = os.listdir(fileName)
                    for card in listdirs:

                        cardGray = cv2.imdecode(np.fromfile(fileName + "\\" + card, dtype=np.uint8), 0)
                        #print(f"cardGray:{cardGray}")
                        #imgs = cv2.blur(imgs, (3, 3))
                        #cardGray = cv2.blur(cardGray, (3, 3))
                        match = cv2.matchTemplate(imgs,cardGray, cv2.TM_CCOEFF_NORMED)
                        locathions = np.where(match >= 0.85)
                        if len(locathions[0]) == 0:
                            #print("没识别到，生成截图")
                            pass
                        else:
                            #print(f"识别到图片：{childFile}")
                            bool = 0
                            self.view_images(fileName + "\\" + card,i,childFile)
                            break



                if bool == 1:

                    w = 49
                    h = 74
                    w1 = 410
                    h1 = 526
                    if i == 0:
                        # 410, 526, 459, 600  49,74
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
                        # 580,527,629,598,宽高(49,71)
                        w = 49
                        h = 71
                        w1 = 580
                        h1 = 527
                    with mss.mss() as sct:
                        hwndWindow = Win32Window(hwnd)
                        # 获取窗口的区域
                        left, top, right, bottom = hwndWindow.left, hwndWindow.top, hwndWindow.right, hwndWindow.bottom
                        box = {"top": top + h1, "left": left + w1, "width": w, "height": h}

                        image_sct = sct.grab(box)
                        im_opencv = np.array(image_sct)
                    sourceimg = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
                    #sourceimg = cv2.blur(sourceimg, (3, 3))



                    print("开始生成截图")
                    # 将当前时间转化为时间戳
                    timestamp = int(time.time())
                    random_number = str(random.randint(0, 10000000))
                    sourceImg = str(timestamp) + random_number + ".tif"

                    # 打印时间戳
                    #print(f"当前时间戳为{timestamp}")

                    pathout = os.path.dirname(path) + "\临时卡牌\\" + sourceImg
                    cv2.imencode('.tif', sourceimg)[1].tofile(pathout)
                    # img1 = cv2.imdecode(np.fromfile("temimg.tif", dtype=np.uint8), 0)
                    self.view_images(pathout, i, "未识别")
                i +=1
                #del imgs,sourceImg
            end_time = time.time()
            logger.info("复制文件运行时间：%.2f秒" % (end_time - start_time))
        except Exception as e:
            logger.info(f"识别失败:{str(e)}")

    def saveImg(self):
       print("保存训练图")
       try:
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
       except Exception as e:
           logger.info(f"保存图片失败:{str(e)}")



class UpdateTpwThread(QThread):
    def run(self):
        logger.info("开始更新辅助")
        os.system('updateTpw.exe')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = TpwMain()
    win.setWindowIcon(QIcon('.\models\\tpwlogo.png'))
    win.show()
    app.exit(app.exec())







