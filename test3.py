import numpy as np
import cv2



font = cv2.FONT_HERSHEY_SIMPLEX
lower_red = np.array([4 / 2, (int)(255 * 0.90), (int)(255 * 0.64)])  # 红色阈值下界
higher_red = np.array([ 10 / 2, 255, 255])  # 红色阈值上界
lower_yellow = np.array([15, 230, 230])  # 黄色阈值下界
higher_yellow = np.array([35, 255, 255])  # 黄色阈值上界
lower_blue = np.array([85,240,140])
higher_blue = np.array([100,255,165])
frame=cv2.imread("yans2.bmp")
img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask_red = cv2.inRange(img_hsv, lower_red, higher_red)  # 可以认为是过滤出红色部分，获得红色的掩膜
mask_yellow = cv2.inRange(img_hsv, lower_yellow, higher_yellow)  # 获得绿色部分掩膜
mask_yellow = cv2.medianBlur(mask_yellow, 7)  # 中值滤波
mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
mask_blue = cv2.inRange(img_hsv, lower_blue, higher_blue)  # 获得绿色部分掩膜
mask_blue = cv2.medianBlur(mask_blue, 7)  # 中值滤波
#mask = cv2.bitwise_or(mask_green, mask_red)  # 三部分掩膜进行按位或运算
print(mask_red)
cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #红色
cnts2, hierarchy2 = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测 #蓝受
cnts3, hierarchy3 = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
print(f"cnts1：{cnts1}")
print(f"cnts2：{cnts2}")
print(f"cnts3：{cnts3}")
for cnt in cnts1:
    (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
    cv2.putText(frame, 'red', (x, y - 5), font, 0.7, (0, 0, 255), 2)
for cnt in cnts2:
    (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
    cv2.putText(frame, 'blue', (x, y - 5), font, 0.7, (0, 0, 255), 2)

for cnt in cnts3:
    (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 将检测到的颜色框起来
    cv2.putText(frame, 'yellow', (x, y - 5), font, 0.7, (0, 255, 0), 2)
cv2.imshow('frame', frame)

cv2.waitKey(0)
cv2.destroyAllWindows()