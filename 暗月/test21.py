import cv2
import numpy as np

template = img = cv2.imdecode(np.fromfile("暗月39蓝牌.bmp", dtype=np.uint8),0) # 加载灰度图像
image = img = cv2.imdecode(np.fromfile("暗月背景c.bmp", dtype=np.uint8),0)  # 加载灰度模板
w, h = template.shape[::-1]  # 获取模板的宽度和高度

res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.70  # 设置匹配阈值
loc = np.where(res >= threshold)

for pt in zip(*loc[::-1]):
    cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)  # 绘制矩形框

cv2.imshow('Detected', image)
cv2.waitKey(0)
cv2.destroyAllWindows()