import time

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

from img1 import calcGrayHist
from opencvImg import img5




#原博客地址：
#https://www.cnblogs.com/yanshw/p/15603757.html
if __name__=="__main__":

    '''
    1.FLANN代表近似最近邻居的快速库。它代表一组经过优化的算法，用于大数据集中的快速最近邻搜索以及高维特征。
    2.对于大型数据集，它的工作速度比BFMatcher快。
    3.需要传递两个字典来指定要使用的算法及其相关参数等
    对于SIFT或SURF等算法，可以用以下方法：
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    对于ORB，可以使用以下参数：
    index_params= dict(algorithm = FLANN_INDEX_LSH,
                       table_number = 6, # 12   这个参数是searchParam,指定了索引中的树应该递归遍历的次数。值越高精度越高
                       key_size = 12,     # 20
                       multi_probe_level = 1) #2
    '''
    # template  = img5.imgHandle("./tag/0604094415.527.tif")
    # target  = img5.imgHandle("./sourceImg/1698746136929545.tif")

    #queryImage = img5.imgHandle("./tag/0604094415.527.tif")
    #trainingImage =img5.imgHandle("./sourceImg/1698746136929545.tif")
    template = cv2.imread("./tag/16940780326215453.tif", cv2.IMREAD_GRAYSCALE)
    gray1 = cv2.equalizeHist(template)

    target = cv2.imread("./sourceImg/16989211163994971.tif", cv2.IMREAD_GRAYSCALE)
    gray2 = cv2.equalizeHist(target)
    start_time = time.time()



    # 读取图片，并转为灰度图

    start_time = time.time()


    # 创建orb对象
    orb = cv2.ORB_create()
    # 对ORB进行检测
    kp1, dst1 = orb.detectAndCompute(gray1, None)
    kp2, dst2 = orb.detectAndCompute(gray2, None)

    # 创建匹配器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    # 描述子进行匹配
    match = bf.match(dst1, dst2)

    img3 = cv2.drawMatches(gray1, kp1, gray2, kp2, match, None)


    end_time = time.time()
    print("FindPicS程序运aaa行时间：%.2f秒" % (end_time - start_time))

    img3 = cv2.drawMatches(gray1, kp1, gray2, kp2, match, None)



    cv2.imshow("aaa",img3)
    cv2.waitKey()

