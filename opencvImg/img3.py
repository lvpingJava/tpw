import cv2
import numpy as np
import sys
from img1 import calcGrayHist



#原博客地址：https://www.cnblogs.com/supershuai/p/12436669.html
#直方图正规化
if __name__=="__main__":
    # 图片转为灰度图
    img = cv2.imread("./sourceImg/16987461343943658.tif", cv2.IMREAD_GRAYSCALE)
    #求出img 的最大最小值
    Maximg = np.max(img)
    Minimg = np.min(img)
    print(Maximg, Minimg, '-----------')
    #输出最小灰度级和最大灰度级
    Omin,Omax = 0,255
    #求 a, b
    a = float(Omax - Omin)/(Maximg - Minimg)
    b = Omin - a*Minimg
    print(a,b,'-----------')
    #线性变换
    O = a*img + b
    O = O.astype(np.uint8)
    #利用灰度直方图进行比较  mget为GrayHist中的写方法
    #calcGrayHist(img)
    #calcGrayHist(O)


    #cv2.imshow('img',img)
    cv2.imshow('enhance',O)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def imgHandle(imgstr):
    # 图片转为灰度图
    img = cv2.imread(imgstr, cv2.IMREAD_GRAYSCALE)
    # 求出img 的最大最小值
    Maximg = np.max(img)
    Minimg = np.min(img)
    print(Maximg, Minimg, '-----------')
    # 输出最小灰度级和最大灰度级
    Omin, Omax = 0, 255
    # 求 a, b
    a = float(Omax - Omin) / (Maximg - Minimg)
    b = Omin - a * Minimg
    print(a, b, '-----------')
    # 线性变换
    O = a * img + b
    O = O.astype(np.uint8)
    # 利用灰度直方图进行比较  mget为GrayHist中的写方法
    # calcGrayHist(img)
    # calcGrayHist(O)
    return O
