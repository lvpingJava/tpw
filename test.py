import os
import cv2
import numpy as np
for p in range(12):
    p = p+1
    img1=cv2.imread(f"149blue{p}.bmp")
    img1gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    template=cv2.imread("149yt12.bmp")
    templategray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    match = cv2.matchTemplate(templategray,img1gray,cv2.TM_CCOEFF_NORMED)
    locathions = np.where(match>=0.86)
    if len(locathions[0]) == 0:
        pass
    else:
        print(f"locathions:{locathions}")
        h,w=img1.shape[0:2]
        for p in zip(*locathions[::-1]):
            x1,y1=p[0],p[1]
            x2,y2=x1+w,y1+h
            cv2.rectangle(template,(x1,y1),(x2,y2),(0,255,0),2)

        cv2.imshow("template2",template)
        cv2.waitKey()

