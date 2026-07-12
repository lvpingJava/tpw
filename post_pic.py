# pip install -r requirements.txt
import win32gui, win32ui, win32con, win32api
import cv2
import numpy as np
from YOLO import Yolo
import time

# 传入窗口句柄，返回图片bytes
def Window_Shot(hwnd):
    if win32gui.IsWindow(hwnd) == False:
        hwnd = win32gui.GetDesktopWindow()
        MoniterDev = win32api.EnumDisplayMonitors(None, None)  # 获取监控器信息
        w = MoniterDev[0][2][2]  # print w,h　　　#图片大小
        h = MoniterDev[0][2][3]
    else:
        ret = win32gui.GetClientRect(hwnd)
        w = ret[2]
        h = ret[3]
    w = 297
    h = 123
    #336,413,760,624,宽高(424,211)
    hwndDC = win32gui.GetWindowDC(hwnd)   # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)    # 根据窗口的DC获取mfcDC
    saveDC = mfcDC.CreateCompatibleDC()    # mfcDC创建可兼容的DC
    saveBitMap = win32ui.CreateBitmap()    # 创建bigmap准备保存图片
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)    # 为bitmap开辟空间
    saveDC.SelectObject(saveBitMap)    # 高度saveDC，将截图保存到saveBitmap
    #saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (w,h), mfcDC, (367,499), win32con.SRCCOPY)    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveBitMap.SaveBitmapFile(saveDC, "adfsdf.jpg")
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
    im_opencv.shape = (h, w, 4)
    cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
    my_bytes = np.array(cv2.imencode('.jpg', im_opencv)[1]).tobytes()
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return my_bytes

if __name__ == '__main__':
    yolo = Yolo()

    while True:
        t1 = time.time()
        ret_list, obj_num, ret = yolo.post_pic(pic_bytes=my_pic, post_url='http://10.50.8.250:7700/pic') # 这里使用的局域网内其他电脑上的检测器进行识别图片http://192.168.2.233:7700/pic
        t2 = time.time()
        time.sleep(0.5)
        jg = ''
        for i in ret_list:
            jg += 'id:' + i.obj_id + '   x:' + i.x + '   y:' + i.y + '   w:' + i.w + '   h:' + i.h + '   prob:' + i.prob + '   name:' + i.name + '\r\n'
        print('【耗时' + str(int((t2-t1)*1000)) + "ms，共" + str(obj_num) + '个目标】\r\n' + '[返回总文本]' + ret + '\r\n' + jg + '\r\n')

