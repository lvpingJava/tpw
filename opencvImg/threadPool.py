import time

import cv2
import os
from concurrent.futures import ThreadPoolExecutor

# 定义全局线程池
global_executor = ThreadPoolExecutor(max_workers=20)
def compare_images(img1_path, img2_path):
    # 加载图片
    img1 = cv2.imread(img1_path, cv2.COLOR_BGR2GRAY)
    img2 = cv2.imread(img2_path, cv2.COLOR_BGR2GRAY)

    img1 = cv2.equalizeHist(img1)
    tag = 1
    if tag == 1:
        clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
        img1 = clahe.apply(img1)

    img2 = cv2.equalizeHist(img2)
    if tag == 1:
        img2 = clahe.apply(img2)


    # 创建SIFT检测器
    sift = cv2.SIFT_create(nfeatures=400)

    # 检测关键点和描述符
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # 暴力匹配器
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.76 * n.distance: # 舍弃大于0.7的匹配
            good.append(m)

    #print( f"识别结果：{len(good)}")

    return len(good)

def batch_compare_images(image_pairs):
    return [global_executor.submit(compare_images, img1_path, img2_path) for img1_path, img2_path in image_pairs]

if __name__ == "__main__":
    image_pairs = []
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/0603164751.757.tif","./sourceImg/16987461282346379.tif"))
    image_pairs.append(("./tag/16940896636273952.tif", "./sourceImg/16987461322140949.tif"))
    image_pairs.append(("./tag/16940896636273952.tif", "./sourceImg/16987461322140949.tif"))
    image_pairs.append(("./tag/16940896636273952.tif", "./sourceImg/16987461322140949.tif"))
    image_pairs.append(("./tag/16940896636273952.tif", "./sourceImg/16987461322140949.tif"))
    image_pairs.append(("./tag/16940893036683741.tif", "./sourceImg/sdfs.bmp"))
    image_pairs.append(("./tag/16940896636273952.tif", "./sourceImg/16987461322140949.tif"))
    image_pairs.append(("./tag/16940896636273952.tif","./sourceImg/16987461322140949.tif"))


    start_time = time.time()
    futures = batch_compare_images(image_pairs)
    print(len(futures))
    for future in futures:
        print(f"Image pair:: {future.result()}")

    end_time = time.time()
    print("FindPicS程序运aaa行时间：%.2f秒" % (end_time - start_time))

