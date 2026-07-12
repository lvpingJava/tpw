
import cv2
import numpy as np


def imgZh(imgName):
    path = "I:\\图片\原图\\" + imgName
    #path = "C:\\test_game\\" + imgName
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8),0)
    #cv2.imshow("img", img)
    #cv2.waitKey(5)
    cv2.imencode('.tif', img)[1].tofile("I:\图片\灰度图\\"+imgName)

imgZh("20251020213227.jpg")



