import cv2
import numpy as np

image = cv2.imread('your_image.jpg', 0)  # 加载灰度图像
template = cv2.imread('your_template.jpg', 0)  # 加载灰度模板
w, h = template.shape[::-1]  # 获取模板的宽度和高度

res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8  # 设置匹配阈值
loc = np.where(res >= threshold)

for pt in zip(*loc[::-1]):
    roi = image[pt[1]:pt[1] + h, pt[0]:pt[0] + w]  # 提取匹配区域的ROI
    roi_color = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)  # 转换为彩色图像以便绘制轮廓
    edges = cv2.Canny(roi, 100, 200)  # 应用Canny边缘检测
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓

    # 绘制所有轮廓
    cv2.drawContours(roi_color, contours, -1, (0, 255, 0), 2)

    # 将ROI放回原图
    image[pt[1]:pt[1] + h, pt[0]:pt[0] + w] = roi_color

cv2.imshow('Detected', image)
cv2.waitKey(0)
cv2.destroyAllWindows()