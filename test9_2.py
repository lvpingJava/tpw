import cv2
import numpy as np
temps = []
for i in range(3):
    temps.append(cv2.imread(f'nums/{i}.png', cv2.IMREAD_GRAYSCALE))


im = cv2.imread('numtest.bmp')
gray = cv2.cvtColor(im, cv2.COLOR_BGRA2GRAY)
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
result = []
for cnt in contours:
    [x,y,w,h] = cv2.boundingRect(cnt)
    # 按照高度筛选
    if 19 >= h >= 7:
        result.append([x,y,w,h])

result.sort(key=lambda x:x[0])

for x, y, w, h in result:
    print("aaaaa")
    # 在画面中标记识别的结果
    cv2.rectangle(im, (x,y),(x+w,y+h),(0,0,255),1)
    digit = cv2.resize(thresh[y:y+h, x:x+w], (14, 20))
    res = []
    for i, t in enumerate(temps):
        match = cv2.matchTemplate(digit, t, cv2.TM_CCORR_NORMED)
        locathions = np.where(match >= 0.8)
        if len(locathions[0]) == 0:
            pass
            # logger.info("未识别到：" + card)
        else:
            res.append((i, match[0]))
            cv2.putText(im, str(f"{res[-1][0]}"), (x, y+35), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            cv2.imshow('Digits OCR Test', im)
            cv2.waitKey(0)
