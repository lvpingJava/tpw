import mouse
import win32gui
import sys
from PySide6.QtWidgets import QApplication,QMainWindow
from PySide6 import QtWidgets
from main_ui import Ui_MainWindow
from PySide6.QtCore import QThread
from game import GameThread
from Plugin import shareData

class MainWindow(QMainWindow):
    pass 
    blistenMouse:bool = False
     #变量
    hwnd = 0
    app:QApplication
    #加载模型
    bStart = False
    gamethd:QThread



    def __init__(self, parent = None) :
        super().__init__(parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_selectWindow.clicked.connect(self.selectWindow)
        self.ui.btn_loadModel.clicked.connect(self.loadModel)
        self.ui.btn_startScan.clicked.connect(self.allStart)
        
    
    def on_mouse_click(self):
        print("Mouse clicked at position")
        #print("Button:", event.button)
        self.blistenMouse = False
        mouse.unhook_all()

    def selectWindow(self):
        '''mouse.on_click(self.on_mouse_click)
        self.blistenMouse = True
        while self.blistenMouse:
            # 获取鼠标的当前位置
            x, y = mouse.get_position()
            print(f"鼠标当前位置：({x}, {y})")
            # 获取鼠标所在窗口的句柄
            self.hwnd = win32gui.WindowFromPoint((x, y))
            print(f"鼠标所在窗口的句柄：{self.hwnd}")
            time.sleep(1)'''

        self.hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "塔防精灵")
        # 获取窗口标题
        title = win32gui.GetWindowText(self.hwnd)
        print(f"窗口标题：{title} 句柄：{self.hwnd}")
        self.ui.label_hwd.setText(f"窗口标题：{title} 句柄：{self.hwnd}")



    def loadModel(self):
        if not shareData.plugin.yoloInitSuccess:
            ret = shareData.plugin.loadYolo()
            # self.ui_showlog(f"模型加载{ret}")
            self.ui.label_loadRet.setText(f"模型加载{ret}")
    

    def allStart(self):
        print(f"mainUI thread= {QThread.currentThread()}")
        self.bStart = not self.bStart
        if self.bStart:
            self.ui.btn_startScan.setText("停止")
            #启动主程序线程
            self.gamethd = GameThread(self.app.primaryScreen(),self.hwnd,self.ui_showlog)
            self.gamethd.bStart = True
            self.gamethd.uiSlot.connect(self.ui_showlog)
            self.gamethd.start()
        else:
            self.ui.btn_startScan.setText("开始")
            print("准备停止线程")
            self.gamethd.bStart = False
            # self.capthd.exit()
    def ui_showlog(self,str):
        self.ui.textBrowser.append(str + "\n")
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.app = app
    win.setWindowTitle("第一个程序")
    win.show()
    app.exit(app.exec())



