import cnocr
import time
import cv2

ocr = cnocr.CnOcr(model_name='densenet_lite_136-fc', cand_alphabet='0123456789')
for i in range(9):
    start_time = time.time()
    i = i +1
    img_path = f'numtest{i}.bmp'
    img= cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    result = ocr.ocr(img)
    end_time = time.time()
    print("识别寒冰船长时间：%.2f秒" % (end_time - start_time))
    print(result)



