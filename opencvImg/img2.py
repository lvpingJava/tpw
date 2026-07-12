import cv2
import numpy as np
import sys
#原博客地址：https://www.cnblogs.com/supershuai/p/12436669.html
#线性变换
if __name__=="__main__":
    #图片转为灰度图
    img = cv2.imread("./sourceImg/16987461283217896.tif",cv2.IMREAD_GRAYSCALE)
    a=2
    #线性变换  定义float类型
    O = float(a)*img
    #数据截取  如果大于255 取 255
    O[0>255] = 255
    #数据类型的转换
    O = np.round(O)
    O = O.astype(np.uint8)
    cv2.imshow("img",img)
    cv2.imshow('enhance',O)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
