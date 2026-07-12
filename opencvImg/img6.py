
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

from img1 import calcGrayHist

# 读取需要特征匹配的两张照片，格式为灰度图
queryImage = cv.imread("./0604094654.178.tif", 0)
trainingImage = cv.imread("./sourceImg/16987461283217896.tif", 0)
#queryImage  = cv.imread("./16940892483425852.tif", 0)
#trainingImage  = cv.imread("./sourceImg/16987461274211743.tif", 0)



sift = cv.SIFT_create()     # 创建sift检测器
kp1, des1 = sift.detectAndCompute(queryImage, None)
kp2, des2 = sift.detectAndCompute(trainingImage, None)
# 设置Flannde参数
FLANN_INDEX_KDTREE = 0
indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
searchParams = dict(checks=50)
flann = cv.FlannBasedMatcher(indexParams, searchParams)     # 建立匹配关系
matches = flann.knnMatch(des1, des2, k=2)                   # 开始匹配
# 设置好初始匹配值
matchesMask = [[0, 0] for i in range(len(matches))]
for i, (m, n) in enumerate(matches):
    if m.distance < 0.5 * n.distance: # 舍弃小于0.5的匹配结果
        matchesMask[i] = [1, 0]
print(matchesMask)

drawParams = dict(matchColor=(0, 0, 255), singlePointColor=(255, 0, 0),
                  matchesMask=matchesMask, flags=0)         # 给特征点和匹配的线定义颜色
resultimage = cv.drawMatchesKnn(queryImage, kp1, trainingImage, kp2,
                                matches, None, **drawParams) # 画出匹配的结果
cv.imshow("aaa",resultimage)
cv.waitKey()
