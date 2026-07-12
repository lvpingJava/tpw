import os
import time
import cv2
import numpy as np
import win32con
import win32gui
import win32ui
from text_det import TextDetector
from text_angle_cls import TextClassifier
from text_rec import TextRecognizer

os.environ["KMP_DUPLICATE_LIB_OK"] = 'TRUE'

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
        self.detect_model = TextDetector()
        self.angle_model = TextClassifier()
        self.rec_model = TextRecognizer()
        print("初始化完成")

    def findOcr(self):
        start_time = time.time()

        srcimg = self.Window_Img(4927408,69,459,537,509,0)


        #srcimg = self.Window_Img(592424, 710, 338, 768, 391, 0)
        #srcimg = self.Window_Img(592424, 700, 437, 775, 500, 0)
        '''srcimg = self.Window_Img(592424, 703, 470, 776, 533, 0)
        end_time = time.time()
        print("aaaagetOcr程序运行时间：%.2f秒" % (end_time - start_time))
        cv2.imshow("template3", srcimg)
        cv2.waitKey()'''
        #srcimg = cv2.imread("yans3.bmp")
        box_list = self.detect_model.detect(srcimg)
        result = ""
        if len(box_list) > 0:
            for point in box_list:
                point = self.detect_model.order_points_clockwise(point)
                textimg = self.detect_model.get_rotate_crop_image(srcimg, point.astype(np.float32))
                angle = self.angle_model.predict(textimg)
                if angle == '180':
                    textimg = cv2.rotate(textimg, 1)
                result = self.rec_model.predict_text(textimg)
                print(result)

        end_time = time.time()
        print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))
        print(result)
        return result


if __name__ == '__main__':
    ocr = pyOcr()
    ocr.__int__()
    ocr.findOcr()
