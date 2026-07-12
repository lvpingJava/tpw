from concurrent.futures import ThreadPoolExecutor
import threading
import time
from queue import Queue
from cv2 import xfeatures2d

import cv2
import numpy as np
lock3 = threading.RLock()
idQueue = Queue(20)
def 图片识别2(a,b):
    start_time = time.time()
    template = cv2.imread("./tag/16940779446177657.tif", cv2.IMREAD_GRAYSCALE)

    target = cv2.imread("./sourceImg/16989211163994971.tif", cv2.IMREAD_GRAYSCALE)

    match = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    locathions = np.where(match >= 0.85)
    if len(locathions[0]) == 0:
        end_time = time.time()
        print("zzzzzzzzzzzzzzzzzzz：%.2f秒" % (end_time - start_time))
        return 0
    else:
        end_time = time.time()
        print("zzzzzzzzzzzzzzzzzzz：%.2f秒" % (end_time - start_time))
        return 1

def 图片识别(a,b):
    MIN_MATCH_COUNT = 9  # 设置最低特征点匹配数量为10
    # 读取需要特征匹配的两张照片，格式为灰度图
    # template  = img5.imgHandle("./tag/16940896636273952.tif")
    # target  = img5.imgHandle("./sourceImg/16987461322630002.tif")
    template = cv2.imread("./tag/16940779446177657.tif", cv2.IMREAD_GRAYSCALE)
    start_time = time.time_ns()
    template = cv2.equalizeHist(template)



    target = cv2.imread("./sourceImg/16989211163994971.tif", cv2.IMREAD_GRAYSCALE)
    target = cv2.equalizeHist(target)
    end_time = time.time_ns()
    print("a：%.2f秒" % (end_time - start_time))

    start_time = time.time_ns()
    # 0604093218.635.tif
    # template = cv2.imread("./cztemp.bmp", 0)
    # target = cv2.imread("./cz1.bmp", 0)

    # Initiate SIFT detector创建sift检测器
    sift = cv2.SIFT_create(nfeatures=50)
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.76 * n.distance:  # 舍弃大于0.7的匹配
            good.append(m)

    end_time = time.time_ns()
    print("a：%.2f秒" % (end_time - start_time))
    print(f"a:{a},b:{b}")
    print(str(a)+"次："+threading.current_thread().name+":识别成功：len(good)"+str(len(good)))
    idQueue.put(1)
    return 1
def 图片识别3(a,b):
    MIN_MATCH_COUNT = 9  # 设置最低特征点匹配数量为10
    # 读取需要特征匹配的两张照片，格式为灰度图
    # template  = img5.imgHandle("./tag/16940896636273952.tif")
    # target  = img5.imgHandle("./sourceImg/16987461322630002.tif")
    template = cv2.imread("./tag/16940779446177657.tif", cv2.IMREAD_GRAYSCALE)
    template = cv2.equalizeHist(template)



    target = cv2.imread("./sourceImg/16989211163994971.tif", cv2.IMREAD_GRAYSCALE)
    target = cv2.equalizeHist(target)

    # 加载图片
    img1 = template
    img2 = target

    # 初始化SURF检测器
    # 注意：在OpenCV 4.x中，你可能需要从opencv_contrib模块中导入SURF
    # 或者使用其他开源的SURF实现
    # surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400)
    # 由于我无法直接访问opencv_contrib或具体的开源实现，这里用假设的surf代替
    start_time = time.time()
    orb = cv2.ORB_create(nfeatures=200,  # 减少特征点数量
                     scaleFactor=1.5,  # 增大尺度因子
                     edgeThreshold=25,  # 减小边缘阈值
                     WTA_K=2)  # 保持默认描述符参数

    # 检测关键点和描述符
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # 创建匹配器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # 进行匹配
    matches = bf.match(des1, des2)

    # 根据距离排序，距离小的是更好的匹配点
    matches = sorted(matches, key=lambda x: x.distance)

    # 绘制前N个匹配
    N = 10  # 可以修改这个数值来增加或减少显示的匹配点数目
    matched_img = cv2.drawMatches(img1, kp1, img2, kp2, matches[:N], None, flags=2)







    good = []
    for m, n in matches:
        if m.distance < 0.76 * n.distance:  # 舍弃大于0.7的匹配
            good.append(m)

    end_time = time.time()
    print("a：%.2f秒" % (end_time - start_time))
    print(f"a:{a},b:{b}")
    print(str(a)+"次："+threading.current_thread().name+":识别成功：len(good)"+str(len(good)))
    idQueue.put(1)
    return 1



pool = ThreadPoolExecutor(max_workers=15)
def getResult():
    result =0
    start_time = time.time()
    futures = []
    for i in range(10):
        future = pool.submit(图片识别,i*1,i*2)
        futures.append(future)

    while True:
        res = idQueue.get()
        if res > 1:
            result = res
            break
        print("res:{res}")

    return result




图片识别(1,1)
#图片识别2(1,1)
#图片识别3(1,1)
#ress= getResult()
#print(f"ffff:{idQueue.get()}")


