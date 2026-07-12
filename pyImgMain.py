
import time
import cv2
import numpy as np
import win32con
import win32gui
import win32ui

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
            #return cv2.cvtColor(im_opencv, cv2.COLOR_RGBA2RGB)
            # cv2.COLOR_BGRA2BGR
            #COLOR_BGRA2BGR
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR)

    def __int__(self):

        print("初始化完成")

    def findOcr(self):
        start_time = time.time()
        #对战
        #srcimg = self.Window_Img(3611532,83,456,102,473,0)
        #srcimg = self.Window_Img(3611532,39,455,58,473,0)
        #srcimg = self.Window_Img(3611532,81,381,98,397,0)
        #srcimg = self.Window_Img(3611532,42,381,59,396,0)
        #srcimg = self.Window_Img(3611532,85,310,104,327,0)
        #srcimg = self.Window_Img(3611532,41,310,58,327,0)
        #srcimg = self.Window_Img(3611532,148,380,165,395,0)


        #合作左边
        #srcimg = self.Window_Img(3936574, 136,459,152,475, 0)
        #srcimg = self.Window_Img(3936574, 98,459,112,473, 0)
        #srcimg = self.Window_Img(3936574, 137,388,152,400, 0)
        #srcimg = self.Window_Img(3936574, 97,385,113,400, 0)
        #srcimg = self.Window_Img(3936574, 137,314,153,329, 0)
        #srcimg = self.Window_Img(3936574, 98,316,113,329, 0)
        #srcimg = self.Window_Img(3936574, 117,238,131,250, 0)

        # 合作右边
        srcimg = self.Window_Img(3936574, 265,459,279,473, 0)
        #srcimg = self.Window_Img(3936574, 229,459,243,474, 0)
        #srcimg = self.Window_Img(3936574, 264,386,277,401, 0)
        #srcimg = self.Window_Img(3936574, 228,387,243,401, 0)
        #srcimg = self.Window_Img(3936574, 264,316,278,330, 0)
        #srcimg = self.Window_Img(3936574, 228,315,243,328, 0)
        #srcimg = self.Window_Img(3936574, 219,239,233,251, 0)

        #srcimg = self.Window_Img(3936574, 317, 347, 362, 380, 0)
        template=cv2.imread("103.bmp", cv2.IMREAD_COLOR)

        match = cv2.matchTemplate(srcimg, template, cv2.TM_CCOEFF_NORMED)
        locathions = np.where(match >= 0.85)
        if len(locathions[0]) == 0:
            pass
        else:
            print("已找到")
        end_time = time.time()
        print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))



if __name__ == '__main__':
    ocr = pyOcr()
    ocr.__int__()
    ocr.findOcr()
