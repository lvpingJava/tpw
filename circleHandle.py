import cv2
import numpy as np
from matplotlib.path import Path
from log import Log
logger = Log().get_log()
#图片处理
def ColorFindContours(srcImage, iLowH, iHighH, iLowS, iHighS, iLowV, iHighV):
    # 转为HSV
    #imgHSV = cv2.cvtColor(srcImage, cv2.COLOR_BGR2HSV)
    bufImg = cv2.inRange(srcImage, np.array((iLowH, iLowS, iLowV)), np.array((iHighH, iHighS, iHighV)))
    return bufImg

def imgHandle(img):
    #img = cv2.imread(imgSrc)
    des = ColorFindContours(img,
        164/2, 174/2,           # 色调最小值~最大值
        90/2, 255,   # 饱和度最小值~最大值
        (int)(255 * 0.9), 255)  # 亮度最小值~最大值
    return des


def getCircle(img,position):

    img = imgHandle(img)
    img = cv2.medianBlur(img, 5)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 180, param1=100, param2=18, minRadius=20, maxRadius=150)
    if circles is None:
        return ""

    circles = np.uint16(np.around(circles))
    logger.info(circles)

    for i in circles[0, :]:
        logger.info(f"检测到点名，坐标：{i[0]}，{ i[1]}")

        '''cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
        cv2.imshow('detected chess', img)
        cv2.moveWindow('detected chess', y=0, x=img.shape[1])
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
        return 寒冰卡牌位置确定(int(i[0])+4,int(i[1])+103,position)


regionInfoLeft1 =None
regionInfoLeft2 =None
regionInfoLeft3 =None
regionInfoLeft4 =None
regionInfoLeft5 =None
regionInfoLeft6 =None
regionInfoLeft7 =None


regionInfoRight1 =None
regionInfoRight2 =None
regionInfoRight3 =None
regionInfoRight4 =None
regionInfoRight5 =None
regionInfoRight6 =None
regionInfoRight7 =None

def 寒冰卡牌区域位置初始化():
    logger.info("寒冰区域坐标初始化")
    global regionInfoLeft1
    global regionInfoLeft2
    global regionInfoLeft3
    global regionInfoLeft4
    global regionInfoLeft5
    global regionInfoLeft6
    global regionInfoLeft7

    global regionInfoRight1
    global regionInfoRight2
    global regionInfoRight3
    global regionInfoRight4
    global regionInfoRight5
    global regionInfoRight6
    global regionInfoRight7

    w1 = 49
    h1 = 65
    x1 = 122
    y1 = 406
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w1 = 51
    h1 = 60
    x1 = 72
    y1 = 406
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft2 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w1 = 51
    h1 = 56
    x1 = 121
    y1 = 332
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft3 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


    w1 = 48
    h1 = 59
    x1 = 71
    y1 = 331
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft4 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


    w1 = 50
    h1 = 56
    x1 = 121
    y1 = 263
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft5 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w1 = 52
    h1 = 63
    x1 = 66
    y1 = 264
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft6 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


    w1 = 46
    h1 = 46
    x1 = 101
    y1 = 204
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoLeft7 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w1 = 48
    h1 = 55
    x1 = 252
    y1 = 411
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 51
    h1 = 64
    x1 = 192
    y1 = 399
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight2 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 52
    h1 = 58
    x1 = 249
    y1 = 336
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight3 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 60
    h1 = 61
    x1 = 193
    y1 = 331
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight4 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 48
    h1 = 55
    x1 = 249
    y1 = 267
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight5 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])
    w1 = 59
    h1 = 63
    x1 = 193
    y1 = 260
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight6 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


    w1 = 49
    h1 = 42
    x1 = 202
    y1 = 206
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    regionInfoRight7 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])


合作战车上卡牌坐标右 = ["271,447", "235,447", "271,375", "235,375", "271,304", "235,304", "227,225"]
合作战车上卡牌坐标左 = ["145,448", "105,448", "145,376", "105,376", "145,303", "105,303", "125,225"]
def 寒冰卡牌位置确定(x,y,position):
    if regionInfoLeft1 is None:
        寒冰卡牌区域位置初始化()
    if position == "左":
        if regionInfoLeft1.contains_point((x, y)):
            logger.info(f"{position}识别位置1")
            return "0"
        if regionInfoLeft2.contains_point((x, y)):
            logger.info(f"{position}识别位置2")
            return "1"
        if regionInfoLeft3.contains_point((x, y)):
            logger.info(f"{position}识别位置3")
            return "2"
        if regionInfoLeft4.contains_point((x, y)):
            logger.info(f"{position}识别位置4")
            return "3"
        if regionInfoLeft5.contains_point((x, y)):
            logger.info(f"{position}识别位置5")
            return "4"
        if regionInfoLeft6.contains_point((x, y)):
            logger.info(f"{position}识别位置6")
            return "5"
        if regionInfoLeft7.contains_point((x, y)):
            logger.info(f"{position}识别位置7")
            return "6"

    elif position == "右":
        if regionInfoRight1.contains_point((x, y)):
            logger.info(f"{position}识别位置1")
            return "0"
        if regionInfoRight2.contains_point((x, y)):
            logger.info(f"{position}识别位置2")
            return "1"
        if regionInfoRight3.contains_point((x, y)):
            logger.info(f"{position}识别位置3")
            return "2"
        if regionInfoRight4.contains_point((x, y)):
            logger.info(f"{position}识别位置4")
            return "3"
        if regionInfoRight5.contains_point((x, y)):
            logger.info(f"{position}识别位置5")
            return "4"
        if regionInfoRight6.contains_point((x, y)):
            logger.info(f"{position}识别位置6")
            return "5"
        if regionInfoRight7.contains_point((x, y)):
            logger.info(f"{position}识别位置7")
            return "6"
    return ""

if __name__=="__main__":
    # 140，272
    # 226，200

    寒冰卡牌位置确定(90+4, 164+103, "左")
    #寒冰卡牌位置确定(145, 448, "左")






