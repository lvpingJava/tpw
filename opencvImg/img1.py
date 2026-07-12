import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
#原博客地址：https://www.cnblogs.com/supershuai/p/12436669.html
#计算灰度直方图
def calcGrayHist(image):
    rows,clos = image.shape
    #创建一个矩阵用于存储灰度值
    grahHist = np.zeros([256],np.uint64)
    #print('这是初始化矩阵')
    #print(grahHist )
    for r in range(rows):
        for c in range(clos):
            #通过图像矩阵的遍历来将灰度值信息放入我们定义的矩阵中
            grahHist[image[r][c]] +=1
    #print('这是赋值后的矩阵')
    #print(grahHist)
    return grahHist
if __name__=="__main__":
    image = cv2.imread("16987178449320666.tif",cv2.IMREAD_GRAYSCALE)
    cv2.imshow("image",image)
    cv2.waitKey()
    grahHist = calcGrayHist(image)
    x_range = range(256)
    plt.plot(x_range,grahHist,'-',linewidth= 3,c='k')
    #设置坐标轴的范围
    y_maxValue = np.max(grahHist)
    plt.axis([0,255,0,y_maxValue])
    #设置标签
    plt.xlabel('gray Level')
    plt.ylabel("number of pixels")
    #显示灰度直方图
    plt.show()
