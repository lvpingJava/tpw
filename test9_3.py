import cv2
import os
import numpy as np
from PIL import Image
import myutils
#绘图展示
def cv_show(name,img):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
def sort_contours(cnts):  # 排序
    i = 1
    boundingBoxes =[cv2.boundingRect(c) for c in cnts]
    cnts,boundingBoxes = zip(*sorted(zip(cnts,boundingBoxes),key=lambda b: b[1][i],reverse=False))
    return cnts
# 已实现合作寒冰关卡识别
# 初始化卷积核
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))

# 模板
image = cv2.imread('./309temp.bmp')
tempimga = myutils.resize(image, width=68,height=20)
tempimg = myutils.resize(image, width=68,height=20)
tempimg = cv2.cvtColor(tempimg, cv2.COLOR_BGR2GRAY)
cv_show('GRAY',tempimg)

refimg = cv2.threshold(tempimg, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_TRIANGLE)[1]
cv_show('threshold',refimg)

#refimg = cv2.threshold(refimg,  0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]

#cv_show('threshold',refimg)

contours, hierarchy = cv2.findContours(refimg.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(tempimga, contours, -1, (0, 0, 255), 2)
cv_show('ref',tempimga)
contours = myutils.sort_contours(contours, method="left-to-right")[0] #排序，从左到右，从上到下
digits = {}  #模板
for (i, c) in enumerate(contours):
    x, y, w, h = cv2.boundingRect(c)
    if (w >= 10 and w <= 50) and (h >= 20 and h <= 30):
        roi = refimg[y:y + h, x:x + w]
        roi = cv2.resize(roi,(22,26))
        digits[i] = roi  #对应模板

print(f"digits大小：{len(digits)}")




# 测试
img = cv2.imread('./309temp.bmp')
tempimga = myutils.resize(img, width=68,height=20)
tempimg = myutils.resize(img, width=68,height=20)
tempimg = cv2.cvtColor(tempimg, cv2.COLOR_BGR2GRAY)
testimg = cv2.threshold(tempimg,  0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]

testcontours, testhierarchy = cv2.findContours(testimg.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(tempimga, testcontours, -1, (0, 0, 255), 2)
cv2.imshow('testimg', tempimga)
cv2.waitKey(0)
testcontours = myutils.sort_contours(testcontours, method="left-to-right")[0] #排序，从左到右，从上到下
groupOutput = []
output = []
for (i, c) in enumerate(testcontours):
    (x, y, w, h) = cv2.boundingRect(c)
    if (w >= 10 and w <= 22) and (h >= 20 and h <= 23):
        roi = testimg[y:y + h, x:x + w]
        print(f"c:{i}")

        roi = cv2.resize(roi,(22,26))
        scores = []
        for (digit, digitROI) in digits.items():
            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)
        groupOutput.append(str(np.argmax(scores)))  # 得到数字
output.extend(groupOutput)
# 输出结果
print("Credit Card #: {}".format("".join(output)))
s = ''.join(groupOutput)  # 将列表拼接为字符串
result = float(s)
formatted_result = format(result, '.3f')  # 格式化结果，保留三位小数
print(formatted_result)
