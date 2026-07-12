import cv2
import numpy as np
import random

def ColorFindContours(srcImage, iLowH, iHighH, iLowS, iHighS, iLowV, iHighV):
    # 转为HSV
    imgHSV = cv2.cvtColor(srcImage, cv2.COLOR_BGR2HSV)
    bufImg = cv2.inRange(imgHSV, np.array((iLowH, iLowS, iLowV)), np.array((iHighH, iHighS, iHighV)))
    return bufImg

def ColorFindContours2(srcImage):
    des1 = ColorFindContours(srcImage,
        350 / 2, 360 / 2,        # 色调最小值~最大值
        (int)(255 * 0.70), 255,  # 饱和度最小值~最大值
        (int)(255 * 0.60), 255)  # 亮度最小值~最大值

    des2 = ColorFindContours(srcImage,
        0, (int)(16 / 2),        # 色调最小值~最大值
        (int)(255 * 0.70), 255,  # 饱和度最小值~最大值
        (int)(255 * 0.60), 255)  # 亮度最小值~最大值

    return des1 + des2


# 以灰度模式载入图像并显示
srcImage = cv2.imread("./opencvImg/cz11.bmp")
# 显示原图
#cv2.imshow("srcImage", srcImage)
#cv2.waitKey(0)

des = ColorFindContours(srcImage,
    164/2, 174/2,           # 色调最小值~最大值
    90/2, 255,   # 饱和度最小值~最大值
    (int)(255 * 0.9), 255)  # 亮度最小值~最大值
cv2.imwrite("./opencvImg/cz11f.bmp",des)
cv2.imshow("des1", des)
cv2.waitKey(0)


#des = ColorFindContours2(srcImage)
#cv2.imshow("des2", des)

cv2.waitKey(0)
cv2.destroyAllWindows()