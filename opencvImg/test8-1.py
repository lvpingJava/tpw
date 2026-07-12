import cv2
import numpy as np
from matplotlib.path import Path
#图片处理
def ColorFindContours(srcImage, iLowH, iHighH, iLowS, iHighS, iLowV, iHighV):
    # 转为HSV
    imgHSV = cv2.cvtColor(srcImage, cv2.COLOR_BGR2HSV)
    bufImg = cv2.inRange(imgHSV, np.array((iLowH, iLowS, iLowV)), np.array((iHighH, iHighS, iHighV)))
    return bufImg

def imgHandle(imgSrc):
    img = cv2.imread(imgSrc)
    des = ColorFindContours(img,
        164/2, 174/2,           # 色调最小值~最大值
        90/2, 255,   # 饱和度最小值~最大值
        (int)(255 * 0.9), 255)  # 亮度最小值~最大值
    return des


def getCircle(srcImg,position):
    img = imgHandle(srcImg)
    img = cv2.medianBlur(img, 5)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 180, param1=100, param2=15, minRadius=20, maxRadius=150)
    if circles is None:
        exit(-1)

    circles = np.uint16(np.around(circles))
    print(circles)

    for i in circles[0, :]:
        print(f"坐标：{i[0]}，{ i[1]}")

        cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
        cv2.imshow('detected chess', img)
        cv2.moveWindow('detected chess', y=0, x=img.shape[1])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return 寒冰卡牌位置确定(i[0],i[1],position)


regionInfoLeft1 =None
regionInfoLeft2 =None
regionInfoLeft3 =None
regionInfoLeft4 =None
regionInfoLeft5 =None
regionInfoLeft6 =None

regionInfoRight1 =None
regionInfoRight2 =None
regionInfoRight3 =None
regionInfoRight4 =None
regionInfoRight5 =None
regionInfoRight6 =None
def 寒冰卡牌区域位置初始化():
    print("寒冰区域坐标初始化")
    global regionInfoLeft1
    global regionInfoLeft2
    global regionInfoLeft3
    global regionInfoLeft4
    global regionInfoLeft5
    global regionInfoLeft6
    global regionInfoRight1
    global regionInfoRight2
    global regionInfoRight3
    global regionInfoRight4
    global regionInfoRight5
    global regionInfoRight6



    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft2 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft3 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft4 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft5 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft6 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight2 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight3 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight4 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight5 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 81
    h1 = 104
    x1 = 392
    y1 = 510
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight6 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


合作战车上卡牌坐标右 = ["271,447", "235,447", "271,375", "235,375", "271,304", "235,304", "227,225"]
合作战车上卡牌坐标左 = ["145,448", "105,448", "145,376", "105,376", "145,303", "105,303", "125,225"]
def 寒冰卡牌位置确定(x,y,position):
    if regionInfoLeft1 is None:
        寒冰卡牌区域位置初始化()
    if position == "left":
        if regionInfoLeft1.contains_point((x, y)):
            return 合作战车上卡牌坐标左[0]
        if regionInfoLeft2.contains_point((x, y)):
            return 合作战车上卡牌坐标左[1]
        if regionInfoLeft3.contains_point((x, y)):
            return 合作战车上卡牌坐标左[2]
        if regionInfoLeft4.contains_point((x, y)):
            return 合作战车上卡牌坐标左[3]
        if regionInfoLeft5.contains_point((x, y)):
            return 合作战车上卡牌坐标左[4]
        if regionInfoLeft6.contains_point((x, y)):
            return 合作战车上卡牌坐标左[5]

    elif position == "right":
        if regionInfoRight1.contains_point((x, y)):
            return 合作战车上卡牌坐标右[0]
        if regionInfoRight2.contains_point((x, y)):
            return 合作战车上卡牌坐标右[1]
        if regionInfoRight3.contains_point((x, y)):
            return 合作战车上卡牌坐标右[2]
        if regionInfoRight4.contains_point((x, y)):
            return 合作战车上卡牌坐标右[3]
        if regionInfoRight5.contains_point((x, y)):
            return 合作战车上卡牌坐标右[4]
        if regionInfoRight6.contains_point((x, y)):
            return 合作战车上卡牌坐标右[5]


# 140，272
# 226，200
position= getCircle("./cz6.bmp","left")
print(f"position：{position}")








