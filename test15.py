#coding:utf-8

import cv2 as cv

img = cv.imread(r"./chinese.png")
img_cvt = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
ret,img_thr = cv.threshold(img_cvt,100,255,cv.THRESH_BINARY)
cv.imshow("img_thr",img_thr)
cv.waitKey(0)
kernel = cv.getStructuringElement(cv.MORPH_RECT,(30,1)) # 由于是1*30的矩阵，字体会被横向空隙的白色腐蚀掉，而下划线横向都是黑色，不会腐蚀
dst = cv.dilate(img_thr,kernel,iterations=1)  # 由于是白底黑字，所有进行膨胀操作来去除黑色字体
cv.imshow("img_thr",img_thr)
cv.imshow("dst",dst)
cv.waitKey(0)
cv.destroyAllWindows()