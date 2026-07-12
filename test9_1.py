import cv2

# 读取图片并转为灰度图
gray = cv2.imread('numtest.bmp', cv2.IMREAD_GRAYSCALE)
# 二值化，cv2.THRESH_OTSU指定由函数判断阈值
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
# 寻找轮廓
contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]

#cv2.drawContours(gray, contours, -1, (0, 0, 255), 3)
#cv2.imshow('tempimg', gray)
#cv2.waitKey(0)

# 将符合要求的轮廓收集并从左到右排序
result = []
for cnt in contours:
    [x,y,w,h] = cv2.boundingRect(cnt)
    if 19 >= h >= 7:
        result.append([x,y,w,h])
result.sort(key=lambda x:x[0])
# 按轮廓截取数字并缩放到14×20大小，导出
count = 0
for x, y, w, h in result:
    #在灰度图中画出轮廓
    cv2.rectangle(gray, (x,y),(x+w,y+h),(0,0,255),1)
    res = cv2.resize(thresh[y:y+h, x:x+w], (14, 20))
    cv2.imwrite(f'nums/{count}.png', res)
    count += 1
# 保存轮廓图
cv2.imwrite("draw_contours.png", gray)