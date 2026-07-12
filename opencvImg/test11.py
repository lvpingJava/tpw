import os
import time

import cv2
import numpy as np

import cv2 as cv

import cv2

import matplotlib.pyplot as plt
start_time = time.time()
src1 = './tag/adfsdfs.tif'
src2 = './sourceImg/1698746134986138.tif'

image1 = cv.imread(src1, cv.IMREAD_GRAYSCALE)
image2 = cv.imread(src2, cv.IMREAD_GRAYSCALE)
img1 = cv.equalizeHist(image1)
img2 = cv.equalizeHist(image2)


orb=cv2.ORB_create()   #创建ORB检测器
kp1,des1=orb.detectAndCompute(img1,None)  #检测关键点和计算描述符
kp2,des2=orb.detectAndCompute(img2,None)  #检测关键点和计算描述符
#定义FLANN参数
FLANN_INDEX_LSH=6
index_params=dict(algorithm=FLANN_INDEX_LSH,
                  table_number=3,
                  key_size=12,
                  multi_probe_level=1)
search_params=dict(checks=50)
flann=cv2.FlannBasedMatcher(index_params,search_params)  #创建FLANN匹配器
matches=flann.match(des1,des2)  #执行匹配操作

end_time = time.time()
print("FindPic程序运行时间：%.2f秒" % (end_time - start_time))

draw_params=dict(matchcolor=(0,255,0),#设置关键点和连接线为绿色
                 singlePointColor=(255,0,0),#设置单个点为红色
                 matchesMask=None,
                 flags=cv2.DrawMatchesFlags_DEFAULT)


img3=cv2.drawMatches(img1,kp1,img2,kp2,matches[:20],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv.imshow("img3", img3)
cv.waitKey()


