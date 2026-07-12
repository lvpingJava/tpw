import cv2
import matplotlib.pyplot as plt

img = cv2.imread('./309temp.bmp')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
min_value=0
#固定阈值
ret,thresh1 = cv2.threshold(gray,min_value,255,cv2.THRESH_BINARY)
ret,thresh2 = cv2.threshold(gray,min_value,255,cv2.THRESH_BINARY_INV)
ret,thresh3 = cv2.threshold(gray,min_value,255,cv2.THRESH_TRUNC)
ret,thresh4 = cv2.threshold(gray,min_value,255,cv2.THRESH_TOZERO)
ret,thresh5 = cv2.threshold(gray,min_value,255,cv2.THRESH_TOZERO_INV)
print("固定阈值：", ret)
#使用了OTSU
ret,thresh11 = cv2.threshold(gray,min_value,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
ret,thresh12 = cv2.threshold(gray,min_value,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
ret,thresh13 = cv2.threshold(gray,min_value,255,cv2.THRESH_TRUNC+cv2.THRESH_OTSU)
ret,thresh14 = cv2.threshold(gray,min_value,255,cv2.THRESH_TOZERO+cv2.THRESH_OTSU)
ret,thresh15 = cv2.threshold(gray,min_value,255,cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)
print("OTSU：", ret)
#使用了TRIANGLE
ret, thresh21 = cv2.threshold(gray, min_value, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
ret, thresh22 = cv2.threshold(gray, min_value, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_TRIANGLE)
ret, thresh23 = cv2.threshold(gray, min_value, 255, cv2.THRESH_TRUNC + cv2.THRESH_TRIANGLE)
ret, thresh24 = cv2.threshold(gray, min_value, 255, cv2.THRESH_TOZERO + cv2.THRESH_TRIANGLE)
ret, thresh25 = cv2.threshold(gray, min_value, 255, cv2.THRESH_TOZERO_INV + cv2.THRESH_TRIANGLE)
print("TRIANGLE：", ret)
titles = ['BINARY','BINARY_INV','TRUNC','TOZERO','TOZERO_INV',
          'BINARY+OTSU','BINARY_INV+OTSU','TRUNC+OTSU','TOZERO+OTSU','TOZERO_INV+OTSU',
          'BINARY+TRI','BINARY_INV+TRI','TRUNC+TRI','TOZERO+TRI','TOZERO_INV+TRI']
images = [thresh1,thresh2,thresh3,thresh4,thresh5,
          thresh11,thresh12,thresh13,thresh14,thresh15,
          thresh21,thresh22,thresh23,thresh24,thresh25]
for i in range(15):
    plt.subplot(3,5,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()
