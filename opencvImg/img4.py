import cv2
import numpy as np
import sys
#原博客地址：https://www.cnblogs.com/supershuai/p/12436669.html
#伽玛变换
if __name__=="__main__":


    # 伽玛变换  power函数实现幂函数

    if __name__ == "__main__":
        # 图片转为灰度图
        img = cv2.imread("./sourceImg/16987461283217896.tif", cv2.IMREAD_GRAYSCALE)
        # 归1
        Cimg = img / 255
        # 伽玛变换
        gamma = 2.5
        O = np.power(Cimg, gamma)
        # 效果
        cv2.imshow('img', img)
        cv2.imshow('O', O)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

