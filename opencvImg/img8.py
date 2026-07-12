import cv2
import numpy as np
from collections import Counter

#圆点检测 原博客地址：
#https://cchang.blog.csdn.net/article/details/81128380?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7EPayColumn-1-81128380-blog-117195622.235%5Ev38%5Epc_relevant_yljh&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7EPayColumn-1-81128380-blog-117195622.235%5Ev38%5Epc_relevant_yljh&utm_relevant_index=1

img = cv2.imread("cz7f.bmp")
# 检测棋子的颜色
def detect_weiqi(img):
    txt = 'black'
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    c = Counter(list(threshold.flatten()))
    print(c.most_common())
    if c.most_common()[0][0] != 0:
        txt = 'white'
    return txt, threshold

#cz4f.bmp
img = cv2.imread("cz9f.bmp")
img = cv2.medianBlur(img, 5)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
'''
1:re_noise时对一幅彩色图片进行处理之后的单通道灰度图片
2:HOUGH_GRADIENT:是使用霍夫梯度法检测圆
3：dp:这个参数是double类型的dp，用来检测圆心的累加器图像的分辨率于输入图像之比的倒数，且此参数允许创建一个比输入图像分辨率低的累加器。
   例如，如果dp= 1时，累加器和输入图像具有相同的分辨率。如果dp=2，累加器便有输入图像一半那么大的宽度和高度
    累加器分辨率与图像分辨率的反比。dp获取越大，累加器数组越小。
4:minDist：检测到的圆的中心，（x,y）坐标之间的最小距离。如果minDist太小，则可能导致检测到多个相邻的圆。如果minDist太大，则可能导致很多圆检测不到。
5:param1:此参数是对应Canny边缘检测的最大阈值，最小阈值是此参数的一半 也就是说像素的值大于param1是会检测为边缘
    用于处理边缘检测的梯度值方法。
6:param2:它表示在检测阶段圆心的累加器阈值。它越小的话，就可以检测到更多根本不存在的圆，而它越大的话，能通过检测的圆就更加接近完美的圆形了
7:minRadius:表示能够检测的最小圆的半径 这里我们设置为0是因为他也要检测圆心 而圆心可以看作是半径为0的圆
8:maxRadius：表示能够检测的最大圆的半径，这里我设置为100，那么表示圆半径大于100的圆不会被检测出来（这个是依据你要检测的图片而考虑）
'''
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 180, param1=100, param2=15, minRadius=20, maxRadius=150)

if circles is None:
    exit(-1)

circles = np.uint16(np.around(circles))
print(circles)

font = cv2.FONT_HERSHEY_SIMPLEX
for i in circles[0, :]:
    print(f"坐标：{i[0]}，{ i[1]}")
    #cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
    cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
    x, y, r = i
    crop_img = img[y - r: y + r, x - r: x + r]
    # 检测围棋
    ''' txt, threshold = detect_weiqi(crop_img)
    print('颜色', '黑色' if txt == 'black' else '白色')

    cv2.putText(threshold, text=txt, org=(0, 0), fontFace=font, fontScale=0.5, color=(0, 255, 0), thickness=2)
    cv2.imshow('threshold', threshold)'''

    cv2.imshow('crop_img', crop_img)
    cv2.moveWindow('crop_img', x=0, y=img.shape[0])

    cv2.imshow('detected chess', img)
    cv2.moveWindow('detected chess', y=0, x=img.shape[1])

    cv2.waitKey(1500)

cv2.waitKey(0)
cv2.destroyAllWindows()





