# -*- coding: utf-8 -*- 
'''
颜色特征识别测试代码
'''
import numpy as np
import cv2
from color_feature import color_block_finder,draw_color_block_rect

def test_color_block_finder_01():
    '''
    色块识别测试样例1 从图片中读取并且识别
    '''

    # 红球阀值：[110   0   0] [255 226 255]   [149 103   0]  [255 255 255]
    # 蓝球阀值：[ 40   0 255]  [ 95 255 255]    [88  0  0]   # [ 96 255 255]

    #[  0 176   0] [  6 255 255]

    # 金色星星 [22 97  0] [255 255 255]      [ 23 136 159] [ 23 255 255] 阀值 给 55
    # [  0 255 192]  [  0 255 255]  金币数值颜色
    for aaaa in range(0):
        print(55555555555555)

    img_path = "demo3-1.bmp"
    # 颜色阈值下界(HSV) lower boudnary
    aaa= "110,0,0"
    aab = aaa.split(",")
    #lowerb =(int(aab[0]),int(aab[1]),int(aab[2]))
    lowerb = (149,103,0)
    # 颜色阈值上界(HSV) upper boundary
    upperb = (255,255,255)

    # 读入素材图片 BGR
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    # 检查图片是否读取成功
    if img is None:
        print("Error: 请检查图片文件路径")
        exit(1)

    # 识别色块 获取矩形区域数组
    rects = color_block_finder(img, lowerb, upperb)
    # 绘制色块的矩形区域
    canvas = draw_color_block_rect(img, rects)
    # 在HighGUI窗口 展示最终结果
    cv2.namedWindow('result', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
    cv2.imshow('result', canvas)

    # 等待任意按键按下
    cv2.waitKey(0)
    # 关闭其他窗口
    cv2.destroyAllWindows()

def test_color_block_finder_02():
    '''
    色块识别测试样例2 从视频流中读取并且识别
    '''
    # 视频路径
    video_path = 'demo-video.mkv'
    # 颜色阈值下界(HSV) lower boudnary
    lowerb = (96, 210, 85) 
    # 颜色阈值上界(HSV) upper boundary
    upperb = (114, 255, 231)


    # 读入视频流
    cap = cv2.VideoCapture(video_path)
    # 色块识别结果展示
    cv2.namedWindow('result', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)

    while(True):
        # 逐帧获取画面
        # ret ？ 画面是否获取成功
        ret, frame = cap.read()
        
        if ret:
            img = frame
            # 识别色块 获取矩形区域数组
            # 同时设定最小高度还有宽度，过滤噪声
            rects = color_block_finder(img, lowerb, upperb,min_w=10,min_h=10)
            # 绘制色块的矩形区域
            canvas = draw_color_block_rect(img, rects)
            # 在HighGUI窗口 展示最终结果 更新画面
            cv2.imshow('result', canvas)

        else:
            print("视频读取完毕或者视频路径异常")
            break

        # 这里做一下适当的延迟，每帧延时0.1s钟
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

def findColor():
    # ... [前面的代码，包括读取图像、转换颜色空间、创建掩码等]

    # 形态学操作
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # 轮廓检测
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 设置最小面积阈值
    min_area = 1000  # 根据实际情况调整

    # 分析轮廓
    valid_image = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            valid_image = True
            # 可以在这里添加更多的条件，比如形状、位置等
            break

    if valid_image:
        print("图片符合要求")
    else:
        print("图片不符合要求")

if __name__ == "__main__":
    # 测试图片色块识别
     test_color_block_finder_01()
    # 测试视频流色块识别
    #test_color_block_finder_02()
