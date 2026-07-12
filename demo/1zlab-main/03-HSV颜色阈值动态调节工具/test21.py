import cv2
import numpy as np

# 读取图像
image = cv2.imread('./demo1-.bmp')

# 高斯模糊
blurred = cv2.GaussianBlur(image, (11, 11), 0)

cv2.imshow('Detected Shape', blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 转换到HSV颜色空间
hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

# 定义颜色的HSV范围（这里以红色为例）  [149 103   0]  [255 255 255]
lower_red = np.array([149, 103, 0])
upper_red = np.array([255, 255, 255])

# 创建掩码
mask = cv2.inRange(hsv, lower_red, upper_red)

# 形态学操作
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# 查找轮廓
contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# 筛选轮廓
min_area = 1500  # 设置一个最小面积阈值
filtered_contours = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area > min_area:
        filtered_contours.append(contour)

# 绘制轮廓
cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 3)

# 显示结果
cv2.imshow('Detected Shape', image)
cv2.waitKey(0)
cv2.destroyAllWindows()