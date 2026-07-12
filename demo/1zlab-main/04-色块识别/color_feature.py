# -*- coding: utf-8 -*- 
'''
颜色特征识别
'''
import numpy as np
import cv2


def color_block_finder(img, lowerb, upperb, 
                        min_w=0, max_w=None, min_h=0, max_h=None):
    '''
    色块识别 返回矩形信息
    '''
    # 转换色彩空间 HSV
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据颜色阈值转换为二值化图像
    img_bin = cv2.inRange(img_hsv, lowerb, upperb)

    # 寻找轮廓（只寻找最外侧的色块）
    contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 设置最小面积阈值
    min_area = 1500  # 根据实际情况调整

    # 分析轮廓
    valid_image = False
    for contour in contours:
        area = cv2.contourArea(contour)
        print(f"area大小：{area}")
        if area > min_area:
            valid_image = True
            # 可以在这里添加更多的条件，比如形状、位置等
            break

    if valid_image:
        print("图片符合要求")
    else:
        print("图片不符合要求")

    # 声明画布 拷贝自img
    canvas = np.copy(img)
    # 外接矩形区域集合
    rects = []

    if max_w is None:
        # 如果最大宽度没有设定，就设定为图像的宽度
        max_w = img.shape[1]
    if max_h is None:
        # 如果最大高度没有设定，就设定为图像的高度
        max_h = img.shape[0]
        
    # 遍历所有的边缘轮廓集合
    for cidx,cnt in enumerate(contours):
        # 获取联通域的外界矩形
        (x, y, w, h) = cv2.boundingRect(cnt)

        if w >= min_w and w <= max_w and h >= min_h and h <= max_h:
            # 将矩形的信息(tuple)添加到rects中
            rects.append((x, y, w, h))
    return rects

def draw_color_block_rect(img, rects,color=(0, 0, 255)):
    '''
    绘制色块的矩形区域
    '''
    # 声明画布(canvas) 拷贝自img
    canvas = np.copy(img)
    # 遍历矩形区域
    for rect in rects:
        (x, y, w, h) = rect
        # 在画布上绘制矩形区域（红框）
        cv2.rectangle(canvas, pt1=(x, y), pt2=(x+w, y+h),color=color, thickness=3)
    
    return canvas