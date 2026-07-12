#原博客地址：https://www.cnblogs.com/supershuai/p/12436669.html
#直方图的均衡化
#计算图像的灰度直方图
#计算灰度直方图的累加直方图
#根据累加的直方图和直方图均衡化的原理得到输入灰度级与输出灰度级之间的映射关系
#使用循环的方式得到输出图像的每一个像素的灰度级
import time

import cv2
import numpy as np
from img1 import calcGrayHist

def imgHandle(imgsr):
    # 图片转为灰度图

    image = cv2.imread(imgsr, cv2.IMREAD_GRAYSCALE)
    rows, cols = image.shape
    # 计算灰度直方图
    grayHist = calcGrayHist(image)
    # 计算累加灰度直方图
    zeroCumuMoment = np.zeros([256], np.uint32)
    for p in range(256):
        if p == 0:
            zeroCumuMoment[p] = grayHist[0]
        else:
            zeroCumuMoment[p] = zeroCumuMoment[p - 1] + grayHist[p]
    # 根据累加的灰度直方图得到输入与输出灰度级之间的映射关系
    output = np.zeros([256], np.uint8)
    cofficient = 256.0 / (rows * cols)
    for p in range(256):
        q = cofficient * float(zeroCumuMoment[p]) - 1
        if q >= 0:
            output[p] = np.math.floor(q)
        else:
            output[p] = 0
    # 得出均衡化图像
    equalHistimg = np.zeros(image.shape, np.uint8)
    for r in range(rows):
        for c in range(cols):
            equalHistimg[r][c] = output[image[r][c]]
    return equalHistimg

#直方图的均衡化
if __name__ == "__main__":
    # 图片转为灰度图
    start_time = time.time()
    image = cv2.imread("./sourceImg/16987461343943658.tif", cv2.IMREAD_GRAYSCALE)

    rows,cols = image.shape
    #计算灰度直方图
    grayHist = calcGrayHist(image)
    #计算累加灰度直方图
    zeroCumuMoment = np.zeros([256], np.uint32)

    for p in range(256):
        if p == 0:
            zeroCumuMoment[p] = grayHist[0]
        else:
            zeroCumuMoment[p] = zeroCumuMoment[p-1] + grayHist[p]

    #根据累加的灰度直方图得到输入与输出灰度级之间的映射关系
    output = np.zeros([256],np.uint8)
    cofficient = 256.0/(rows*cols)
    for p in range(256):
        q = cofficient * float(zeroCumuMoment[p])-1
        if q >=0:
            output[p] = np.math.floor(q)
        else:
            output[p] = 0
    #得出均衡化图像
    equalHistimg = np.zeros(image.shape,np.uint8)

    for r in range(rows):
        for c in range(cols):
            equalHistimg[r][c] = output[image[r][c]]

    end_time = time.time()
    print("FindPic程序运行时间：%.2f秒" % (end_time - start_time))
    wks=[equalHistimg,1,equalHistimg]
    my_dict = {'悟空': wks, '小鹿': equalHistimg}


    #cv2.imshow('image',image)
    cv2.imshow('histimage', my_dict['悟空'][0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()




