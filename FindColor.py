import numpy as np
import cv2
# H 色调最小值~最大值(iLowH~ iHighH)
# S 饱和度最小值~最大值(iLowS~ iHighS)
# V 亮度最小值~最大值(iLowV~ iHighV)
def findColor(hwd:int,iLowH:int, iHighH:int, iLowS:int, iHighS:int, iLowV:int, iHighV:int):
    source = cv2.imread("yans6.bmp")
    lower = np.array([iLowH, iLowS, iLowV])  # 阈值下界
    higher= np.array([iHighH, iHighS, iHighV])  # 阈值上界
    img_hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img_hsv, lower, higher)  # 获得掩膜
    mask= cv2.medianBlur(mask, 7)  # 中值滤波
    cnts1, hierarchy1 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测

    font = cv2.FONT_HERSHEY_SIMPLEX
    for cnt in cnts1:
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        cv2.rectangle(source, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
        cv2.putText(source, '1', (x, y - 5), font, 0.5, (0, 0, 255), 2)
    cv2.imshow('frame', source)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(cnts1) == 0:
        return 0
    else:
        return 1
getresult =  findColor(0, 0, 0, 0, 255, (int)(255 * 0.90), 255)
#getresult =  findColor(0, 0, 0, (int)(255 * 0.99), 255, (int)(255 * 0.64), 255)
#getresult =  FindColor(0, 2, 5, (int)(255 * 0.90), 255, (int)(255 * 0.64), 255)
print(f"getresult:{getresult}")
