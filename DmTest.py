import ctypes
import os
import time

import win32com
import win32gui
from win32com.client import Dispatch

from ctypes import *

import DmTool
from fcnS import FcnS


class OpTest:
    def __init__(self):

        print("init");

    def test_base(self):
        # 输出插件版本号
        print("op ver:", self.op.Ver());
        print("path:", self.op.GetPath());
        self.op.SetShowErrorMsg(2);
        r = self.op.WinExec("notepad", 1);
        print("Exec notepad:", r);

    def test_window_api(self):
        # 测试窗口接口

        self.send_hwnd = 535064
        self.hwnd = 535064
        return 0;

    def test_bkmode(self):
        r = self.op.BindWindow(self.hwnd, "gdi", "normal", "normal", 0);
        if r == 0:
            print("bind false");
        return r;

    def test_bkmouse_bkkeypad(self):
        self.op.MoveTo(200, 200);
        self.op.Sleep(200);
        self.op.LeftClick();
        self.op.Sleep(1000);
        r = self.op.SendString(self.send_hwnd, "Hello World!");
        print("SendString ret:", r);
        self.op.Sleep(1000);
        return 0;

    def test_bkimage(self):
        cr = self.op.GetColor(30, 30);
        print("color of (30,30):", cr);
        ret = self.op.Capture(0, 0, 2000, 2000, "screen.bmp");
        print("op.Capture ret:", ret);
        r, x, y = self.op.FindPic(0, 0, 100, 100, "test.png", "000000", 1.0, 0);
        print("op.FindPic:", r, x, y);
        return 0;

    def test_ocr(self):
        start_time = time.time()
        s1 = self.op.OcrAuto(425,366,502,387, 0.5)
        end_time = time.time()
        print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))
        print(f"s1:{s1}")
        start_time = time.time()
        s1 = self.op.OcrAuto(425,366,502,387, 0.5)
        end_time = time.time()
        print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))
        print(f"s2:{s1}")
        return 0

    def test_clear(self):
        self.op.UnBindWindow();

    def bindGame(self):
        opdll = ctypes.windll.LoadLibrary("./DmReg.dll")
        opdll.RegDll.Reg("./dm.dll")
        dm = win32com.client.Dispatch('dm.dmsoft')
        print(dm.ver())  # 输出版本号

    def test(self):
        res = self.op.Capture(693,586,779,628, "screen.bmp")
        print(f"ressss:{res}")
        for i in range(1000):
            time.sleep(0.5)
            intX = 0
            intY = 0
            res = self.op.FindColor(693,586,779,628, "fe0000-202020", 0.75, 0,intX,intY)
            print(intX)
            print(intY)
            if res == 1:
                print("找到了")
            else:
                print("111111111111111111")

        #res = DmTool.FindPic(self.hwnd, "绿色星星.tif", 27,332,152,467, 0.8, 1)
        #res = DmTool.FindStr(self.hwnd,"刷新",296,566,353,595)
        #stfs="小鹿|萨满|海妖|冰骑|死神|地精|斧客|绿弓|电法|骨弓"
        #res = DmTool.FindPicS(self.hwnd, stfs.split("|"), 392,512,646,614, 0.8)
        #print(f"结果为：{res}")
        #objfns = FcnS()
        #objfns.cardHandler("resCards")










demo = OpTest();
demo.bindGame()
#demo.test()


