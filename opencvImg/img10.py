import cv2 as cv
import numpy as np


img = cv.imread("./cz1.bmp")
img2 = img.copy()                               # a copy of original image
mask = np.zeros(img.shape[:2], dtype = np.uint8) # mask initialized to PR_BG
output = np.zeros(img.shape, np.uint8)           # output image to be shown

rect_or_mask = 0

rect=(2,1,img.shape[0],img.shape[1])
bgdmodel = np.zeros((1, 65), np.float64)
fgdmodel = np.zeros((1, 65), np.float64)
cv.grabCut(img2, mask, rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_RECT)
mask2 = np.where((mask==1) + (mask==3), 255, 0).astype('uint8')
output = cv.bitwise_and(img2, img2, mask=mask2)

cv.imshow('output', output)
cv.imshow('input', img)

cv.waitKey(0)
cv.destroyAllWindows()
