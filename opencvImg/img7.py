import os
import time
import multiprocessing
from multiprocessing import Pool, Manager

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

from img1 import calcGrayHist
from opencvImg import img5
from test12 import 卡牌位置判断


# 特征缓存字典，用于存储模板的特征点和描述符
feature_cache = None

# 定义全局变量用于并行处理
MATCH_POOL = None


def init_pool():
    """初始化进程池"""
    global MATCH_POOL, feature_cache
    from multiprocessing import Manager
    
    # 初始化特征缓存
    if feature_cache is None:
        feature_cache = Manager().dict()
    
    # 初始化进程池
    if MATCH_POOL is None or MATCH_POOL._state != multiprocessing.pool.RUN:
        MATCH_POOL = Pool(processes=min(4, multiprocessing.cpu_count()))


def close_pool():
    """关闭进程池"""
    global MATCH_POOL
    if MATCH_POOL is not None:
        MATCH_POOL.close()
        MATCH_POOL.join()
        MATCH_POOL = None


def match_single_region(region, template_processed, des1, target_processed):
    """
    匹配单个卡牌区域
    :param region: 卡牌区域坐标 (x, y, w, h)
    :param template_processed: 预处理后的模板图像
    :param des1: 模板的描述符
    :param target_processed: 预处理后的目标图像
    :return: (匹配数量, 区域坐标, 匹配数据)
    """
    import cv2
    MIN_MATCH_COUNT = 9
    x, y, w, h = region
    
    # 确保区域在图像范围内
    x = max(0, x)
    y = max(0, y)
    w = min(w, target_processed.shape[1] - x)
    h = min(h, target_processed.shape[0] - y)
    
    if w <= 0 or h <= 0:
        return (0, region, None)
    
    # 提取卡牌区域
    card_roi = target_processed[y:y+h, x:x+w]
    
    # 在子进程内部创建SIFT提取器
    sift = cv2.SIFT_create()
    
    # 计算目标区域的特征
    kp2, des2 = sift.detectAndCompute(card_roi, None)
    
    if des2 is None or len(kp2) < MIN_MATCH_COUNT:
        return (0, region, None)
    
    # 使用FLANN匹配器进行特征匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=30)  # 减少checks数量以提高速度
    flann = cv.FlannBasedMatcher(index_params, search_params)
    
    try:
        matches = flann.knnMatch(des1, des2, k=2)
    except:
        return (0, region, None)
    
    # 应用Lowe's比率测试
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    
    if len(good) < MIN_MATCH_COUNT:
        return (len(good), region, None)
    
    # 计算变换矩阵
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    
    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    if M is None:
        return (len(good), region, None)
    
    return (len(good), region, (good, kp2, M, mask, card_roi))


def imgHandle(imgsr1, imgsr2):
    """
    优化后的图像匹配函数，用于识别不规则球状卡牌
    :param imgsr1: 模板图像路径
    :param imgsr2: 目标图像路径
    :return: 匹配结果 (1: 匹配成功, 0: 匹配失败)
    """
    init_pool()
    
    MIN_MATCH_COUNT = 9  # 设置最低特征点匹配数量为10
    
    try:
        # 读取模板图像
        template = cv.imdecode(np.fromfile(imgsr1, dtype=np.uint8), 0)
        # 读取目标图像
        target = cv.imread(imgsr2, cv.IMREAD_GRAYSCALE)
        
        if template is None or target is None:
            print("图像读取失败")
            return 0
        
        # 图像预处理
        template_processed = imgPreprocessor(template, is_template=True)
        target_processed = imgPreprocessor(target, is_template=False)
        
        # 检测目标图像中的圆形卡牌区域
        card_regions = detectCircularCards(target_processed)
        
        if not card_regions:
            print("未检测到圆形卡牌区域")
            return 0
        
        # 特征提取
        sift = cv.SIFT_create(nfeatures=300, contrastThreshold=0.01, edgeThreshold=10)
        
        # 从缓存中获取模板特征，否则计算并缓存
        template_key = os.path.basename(imgsr1)
        if template_key in feature_cache:
            kp1, des1 = feature_cache[template_key]
        else:
            kp1, des1 = sift.detectAndCompute(template_processed, None)
            feature_cache[template_key] = (kp1, des1)
        
        # 并行处理多个卡牌区域
        results = []
        for region in card_regions:
            result = MATCH_POOL.apply_async(
                match_single_region,
                args=(region, template_processed, des1, target_processed)
            )
            results.append(result)
        
        # 收集匹配结果
        best_match = 0
        best_match_data = None
        best_region = None
        
        for result in results:
            match_count, region, data = result.get()
            if match_count > best_match and data is not None:
                best_match = match_count
                best_match_data = data
                best_region = region
        
        if best_match >= MIN_MATCH_COUNT and best_region:
            x, y, w, h = best_region
            good, kp2, M, mask, card_roi = best_match_data
            
            # 绘制匹配结果
            matchesMask = mask.ravel().tolist()
            h_tpl, w_tpl = template_processed.shape
            pts = np.float32([[0, 0], [0, h_tpl-1], [w_tpl-1, h_tpl-1], [w_tpl-1, 0]]).reshape(-1, 1, 2)
            dst = cv.perspectiveTransform(pts, M)
            
            # 调整坐标到原图像
            dst[:, :, 0] += x
            dst[:, :, 1] += y
            
            # 在原目标图像上绘制结果
            cv.polylines(target, [np.int32(dst)], True, 0, 2, cv.LINE_AA)
            
            # 计算目标坐标
            center_x = x + w // 2 + 385
            center_y = y + h // 2 + 511
            destinationy = [f"{center_x}:{center_y}"]
            
            # 调用卡牌位置判断函数
            卡牌位置判断(destinationy)
            
            # 绘制匹配点
            draw_params = dict(matchColor=(0, 255, 0),
                               singlePointColor=None,
                               matchesMask=matchesMask,
                               flags=2)
            
            # 创建ROI的彩色版本用于显示
            roi_color = cv.cvtColor(card_roi, cv.COLOR_GRAY2BGR)
            result_img = cv.drawMatches(template_processed, kp1, roi_color, kp2, good, None, **draw_params)
            
            # 在主线程中显示结果（避免多线程问题）
            cv.imshow("卡牌匹配结果", result_img)
            cv.waitKey(3)
            
            return 1
        
        print(f"特征匹配个数：{best_match}/{MIN_MATCH_COUNT}")
        return 0
        
    except Exception as e:
        print(f"图像匹配过程中发生错误: {e}")
        return 0

def imgPreprocessor(image, is_template=False):
    """
    优化的图像预处理函数，用于处理渐现效果和不规则形状
    :param image: 输入图像
    :param is_template: 是否为模板图像
    :return: 预处理后的图像
    """
    # 1. 中值滤波去噪
    denoised = cv.medianBlur(image, 3)
    
    # 2. 动态对比度增强（CLAHE）
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # 3. 处理渐现效果：自适应亮度调整
    # 计算图像的平均亮度
    mean_brightness = np.mean(image)
    
    # 根据亮度调整对比度和亮度
    if mean_brightness < 80:  # 较暗的图像（可能是渐现初期）
        # 增强亮度和对比度
        alpha = 1.5  # 对比度增益
        beta = 30    # 亮度增益
        adjusted = cv.convertScaleAbs(enhanced, alpha=alpha, beta=beta)
    elif mean_brightness > 180:  # 较亮的图像（可能是渐现后期）
        # 稍微降低亮度，增强对比度
        alpha = 1.2
        beta = -10
        adjusted = cv.convertScaleAbs(enhanced, alpha=alpha, beta=beta)
    else:
        adjusted = enhanced
    
    # 4. 拉普拉斯边缘增强，突出渐现卡牌的轮廓
    laplacian = cv.Laplacian(adjusted, cv.CV_64F, ksize=3)
    laplacian = np.uint8(np.absolute(laplacian))
    enhanced_edges = cv.addWeighted(adjusted, 0.7, laplacian, 0.3, 0)
    
    # 5. 动态阈值处理
    # 使用自适应阈值处理不同透明度的区域
    if is_template:
        # 模板图像使用OTSU阈值
        _, thresholded = cv.threshold(enhanced_edges, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    else:
        # 目标图像使用自适应阈值，更好地处理渐现效果
        thresholded = cv.adaptiveThreshold(
            enhanced_edges, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv.THRESH_BINARY, 11, 2
        )
    
    # 6. 形态学操作，填补卡牌内部的空洞
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    processed = cv.morphologyEx(thresholded, cv.MORPH_CLOSE, kernel)
    
    # 7. 边缘检测，确保渐现卡牌的轮廓清晰
    edges = cv.Canny(processed, 50, 150)
    processed = cv.bitwise_or(processed, edges)
    
    return processed


def detectCircularCards(image, min_radius=20, max_radius=100):
    """
    检测图像中的圆形/椭圆形卡牌
    :param image: 输入图像
    :param min_radius: 最小半径
    :param max_radius: 最大半径
    :return: 检测到的卡牌区域列表 [(x, y, w, h), ...]
    """
    # 使用霍夫圆变换检测圆形
    circles = cv.HoughCircles(
        image, 
        cv.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=min_radius * 2, 
        param1=100, 
        param2=30, 
        minRadius=min_radius, 
        maxRadius=max_radius
    )
    
    card_regions = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # 添加一定的边界，确保包含整个卡牌
            card_regions.append((x - r, y - r, 2 * r, 2 * r))
    
    # 如果霍夫圆变换没有检测到足够的圆形，使用轮廓检测
    if len(card_regions) < 1:
        # 查找轮廓
        contours, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # 计算轮廓的面积和周长
            area = cv.contourArea(contour)
            perimeter = cv.arcLength(contour, True)
            
            if perimeter == 0:
                continue
            
            # 计算圆形度（圆形度越接近1越圆）
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # 过滤掉非圆形区域
            if 0.7 < circularity < 1.3:  # 允许一定的椭圆度
                # 获取最小外接矩形
                x, y, w, h = cv.boundingRect(contour)
                
                # 过滤掉太小或太大的区域
                if min_radius < w < max_radius * 2 and min_radius < h < max_radius * 2:
                    card_regions.append((x, y, w, h))
    
    return card_regions

def imgsSift():
    # cardImgs = []
    # cardImgs.append("1")
    # cardImgs.append("3")
    # cardImgs.append("4")
    # for index, item in enumerate(cardImgs, start=0):
    #     print(f"sdfsfsdf:{item},,,,,{index}")
    #     print(f"AAAAAA:{cardImgs[index]},,,,,{index}")

    siftCount = 0
    fileName3 = "I:\\tpw2\\opencvImg\\sourceImg"
    listdirs3 = os.listdir(fileName3)

    fileName4 = "I:\\tpw2\\opencvImg\\tag"
    listdirs4 = os.listdir(fileName4)
    MIN_MATCH_COUNT = 9  # 设置最低特征点匹配数量为10
    sift = cv.SIFT_create(nfeatures=350)
    for file3 in listdirs3:
        target = cv.imdecode(np.fromfile(fileName3 + '\\' + file3, dtype=np.uint8), 0)
        for file4 in listdirs4:
            template = cv.imdecode(np.fromfile(fileName4 + '\\' + file4, dtype=np.uint8), 0)

            match = cv.matchTemplate(target, template, cv.TM_CCOEFF_NORMED)
            locathions = np.where(match >= 0.86)
            if len(locathions[0]) == 0:
                pass
            else:

                start_time = time.time()
                # 读取需要特征匹配的两张照片，格式为灰度图
                # template  = img5.imgHandle("./tag/16940896636273952.tif")
                # target  = img5.imgHandle("./sourceImg/16987461322630002.tif")

                # template = imgHadler(template)

                template = cv.equalizeHist(template)
                tag = 1
                if tag == 1:
                    # clipLimit=7  识别138个  clipLimit=7  识别121个
                    clahe = cv.createCLAHE(clipLimit=7, tileGridSize=(8, 8))
                    template = clahe.apply(template)

                # alpha = 1.5  # 增加对比度
                # beta = 10  # 增加亮度
                # template = cv.convertScaleAbs(template, alpha=alpha, beta=beta)


                target = cv.equalizeHist(target)

                if tag == 1:
                    target = clahe.apply(target)
                # target = cv.convertScaleAbs(target, alpha=alpha, beta=beta)

                # target = imgHadler(target)

                # 0604093218.635.tif
                # template = cv.imread("./cztemp.bmp", 0)
                # target = cv.imread("./cz1.bmp", 0)

                # Initiate SIFT detector创建sift检测器

                # find the keypoints and descriptors with SIFT
                kp1, des1 = sift.detectAndCompute(template, None)
                kp2, des2 = sift.detectAndCompute(target, None)

                # 创建设置FLANN匹配
                # FLANN_INDEX_KDTREE =0
                # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                # search_params = dict(checks=50)
                # flann = cv.FlannBasedMatcher(index_params, search_params)
                # matches = flann.knnMatch(des1, des2, k=2)

                # 暴力匹配器
                bf = cv.BFMatcher()
                matches = bf.knnMatch(des1, des2, k=2)

                # store all the good matches as per Lowe's ratio test.
                good = []
                for m, n in matches:
                    if m.distance < 0.60 * n.distance:  # 舍弃大于0.7的匹配
                        good.append(m)

                end_time = time.time()
                #print("FindPicS程序运aaa行时间：%.2f秒" % (end_time - start_time))
                # if len(good) >= 4:
                #     print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
                if 1==2: #len(good) >= MIN_MATCH_COUNT:
                    # 获取关键点的坐标
                    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                    # 计算变换矩阵和MASK
                    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
                    matchesMask = mask.ravel().tolist()
                    h, w = template.shape
                    # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
                    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                    dst = cv.perspectiveTransform(pts, M)
                    cv.polylines(target, [np.int32(dst)], True, 0, 2, cv.LINE_AA)

                else:
                    #print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
                    matchesMask = None

                draw_params = dict(matchColor=(0, 255, 0),
                                   singlePointColor=None,
                                   matchesMask=matchesMask,
                                   flags=2)
                if len(good) >= MIN_MATCH_COUNT:
                    siftCount = siftCount + 1
                    # result = cv.drawMatches(template, kp1, target, kp2, good, None, **draw_params)
                    # cv.imshow("aaa", result)
                    # cv.waitKey()
    print(f"总共识别个数为：{siftCount}")
#原博客地址：
#https://www.cnblogs.com/yanshw/p/15603757.html
if __name__=="__main__":
    #imgsSift()

    MIN_MATCH_COUNT = 10 # 设置最低特征点匹配数量为10
    # 读取需要特征匹配的两张照片，格式为灰度图
    #template  = img5.imgHandle("./tag/16940896636273952.tif")
    #target  = img5.imgHandle("./sourceImg/16987461322630002.tif")
    start_time = time.time()
    template = cv.imread("./tag/0603165045.259.tif", cv.COLOR_BGR2GRAY)
    #template = imgHadler(template)

    template = cv.equalizeHist(template)
    tag = 1
    if tag == 1:
        clahe = cv.createCLAHE(clipLimit=7, tileGridSize=(8, 8))
        template = clahe.apply(template)



    #alpha = 1.5  # 增加对比度
    #beta = 10  # 增加亮度
    #template = cv.convertScaleAbs(template, alpha=alpha, beta=beta)



    target = cv.imread("./sourceImg/sdfs.bmp", cv.COLOR_BGR2GRAY)

    target = cv.equalizeHist(target)

    if tag == 1:
        target = clahe.apply(target)
    #target = cv.convertScaleAbs(target, alpha=alpha, beta=beta)

    #target = imgHadler(target)







    #0604093218.635.tif
    #template = cv.imread("./cztemp.bmp", 0)
    #target = cv.imread("./cz1.bmp", 0)


    # Initiate SIFT detector创建sift检测器
    sift = cv.SIFT_create(nfeatures=350)
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)

    # 创建设置FLANN匹配
    # FLANN_INDEX_KDTREE =0
    # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # search_params = dict(checks=50)
    # flann = cv.FlannBasedMatcher(index_params, search_params)
    # matches = flann.knnMatch(des1, des2, k=2)

    # 暴力匹配器
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.73 * n.distance: # 舍弃大于0.7的匹配
            good.append(m)

    end_time = time.time()
    print("FindPicS程序运aaa行时间：%.2f秒" % (end_time - start_time))
    print( "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        #计算变换矩阵和MASK
        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([ [0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0] ]).reshape(-1, 1, 2)
        dst = cv.perspectiveTransform(pts, M)
        cv.polylines(target, [np.int32(dst)], True, 0, 2, cv.LINE_AA)

    else:
        print( "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
        matchesMask = None


    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv.drawMatches(template, kp1, target, kp2, good, None, **draw_params)
    cv.imshow("aaa",result)
    cv.waitKey()



def test_performance(template_path, target_path, iterations=10):
    """
    测试代码性能
    :param template_path: 模板图像路径
    :param target_path: 目标图像路径
    :param iterations: 测试迭代次数
    :return: 性能测试结果
    """
    print(f"\n=== 性能测试开始 ===")
    print(f"模板图像: {template_path}")
    print(f"目标图像: {target_path}")
    print(f"测试迭代次数: {iterations}")
    
    # 预热
    imgHandle(template_path, target_path)
    
    # 测试预处理性能
    start_time = time.time()
    target = cv.imread(target_path, cv.IMREAD_GRAYSCALE)
    for _ in range(iterations):
        imgPreprocessor(target, is_template=False)
    preprocess_time = (time.time() - start_time) / iterations
    print(f"平均预处理时间: {preprocess_time:.4f} 秒")
    
    # 测试形状检测性能
    target_processed = imgPreprocessor(target, is_template=False)
    start_time = time.time()
    for _ in range(iterations):
        detectCircularCards(target_processed)
    detection_time = (time.time() - start_time) / iterations
    print(f"平均形状检测时间: {detection_time:.4f} 秒")
    
    # 测试整体匹配性能
    start_time = time.time()
    success_count = 0
    for _ in range(iterations):
        result = imgHandle(template_path, target_path)
        if result == 1:
            success_count += 1
    total_time = time.time() - start_time
    avg_time = total_time / iterations
    success_rate = success_count / iterations * 100
    
    print(f"平均匹配时间: {avg_time:.4f} 秒")
    print(f"成功匹配次数: {success_count}/{iterations} ({success_rate:.1f}%)")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"=== 性能测试结束 ===")
    
    return {
        'preprocess_time': preprocess_time,
        'detection_time': detection_time,
        'avg_match_time': avg_time,
        'success_rate': success_rate,
        'total_time': total_time
    }


def visualize_preprocessing(image_path):
    """
    可视化图像预处理效果
    :param image_path: 图像路径
    """
    # 读取图像
    image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    if image is None:
        print("图像读取失败")
        return
    
    # 显示原始图像
    cv.imshow("原始图像", image)
    
    # 预处理
    processed = imgPreprocessor(image, is_template=False)
    
    # 显示预处理后的图像
    cv.imshow("预处理后图像", processed)
    
    # 显示形状检测结果
    card_regions = detectCircularCards(processed)
    image_with_detections = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    
    for (x, y, w, h) in card_regions:
        cv.rectangle(image_with_detections, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv.imshow("形状检测结果", image_with_detections)
    
    cv.waitKey(0)
    cv.destroyAllWindows()


# 使用示例
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    # 示例用法
    # template_path = "path/to/template.jpg"
    # target_path = "path/to/target.jpg"
    
    # # 可视化预处理效果
    # visualize_preprocessing(target_path)
    
    # # 测试性能
    # test_performance(template_path, target_path)
    
    # # 进行匹配
    # result = imgHandle(template_path, target_path)
    # print(f"匹配结果: {'成功' if result == 1 else '失败'}")
    template = "./tag/16940872853611784.tif"
    target = "./sourceImg/16987461299724500.tif"

    # 可视化预处理效果
    visualize_preprocessing(template)

    # 测试性能
    template_path = template
    target_path = target
    test_performance(template_path, target_path, iterations=10)

    # 进行匹配
    result = imgHandle(template_path, target_path)
    print(f"匹配结果: {'成功' if result == 1 else '失败'}")
    # 关闭进程池
    close_pool()

