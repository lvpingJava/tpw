import os
import numpy as np
import cv2
current_dir = os.getcwd()
print(current_dir)
template=cv2.imread("df.jpg",0)
cv2.imshow("template3", template)
cv2.waitKey()

template=cv2.imread("AAAA.tif",0)
fileName = "I:\Program Files\withfriends\塔防老马助手\手牌\霸王"
listdirs = os.listdir(fileName)
for file in listdirs:
        print(f"file:{file}")
        #imgs = cv2.imread(fileName+'\\'+file)
        aaaa= np.fromfile(fileName+'\\'+file, dtype=np.uint8)
        print(f"ff:{aaaa}")
        cv_img = cv2.imdecode(np.fromfile(fileName+'\\'+file, dtype=np.uint8), 0)
        img1gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        cv2.imshow("template2", cv_img)
        cv2.waitKey()
        match = cv2.matchTemplate(template, cv_img, cv2.TM_CCOEFF_NORMED)