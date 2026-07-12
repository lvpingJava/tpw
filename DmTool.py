import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
import win32api
import win32gui, win32ui
import win32con
import time
import os
import mss
import re
from base64 import b64encode
from matplotlib.path import Path
from pygetwindow import Win32Window
from circleHandle import getCircle
from log import Log
from queue import Queue
cardQueue = Queue(30)
logger = Log().get_log()
lock = threading.RLock()
lock3 = threading.RLock()
lock4 = threading.RLock()
path = os.path.dirname(os.path.realpath(__file__))
pool = ThreadPoolExecutor(max_workers=20)

def Window_Img(hwnd: int, x: int, y: int, x1: int, y1: int,types:int,back:int):
    if back != 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
            hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
            saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
            saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
            saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap
            saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)  # 截取从左上角（0，0）长宽为（w，h）的图片
            signedIntsArray = saveBitMap.GetBitmapBits(True)
            im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
            im_opencv.shape = (h, w, 4)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        if types == 1:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
        elif types == 2:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR)
        elif types == 3:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGR2HSV)
            #return cv2.cvtColor(im_opencv, cv2.COLOR_RGBA2RGB)
    elif back == 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
            #width, height = right - left, bottom - top

            # COLOR_BGR2GRAY COLOR_BGRA2BGR COLOR_BGR2HSV
            # 设置截图区域的坐标和尺寸
            with mss.mss() as sct:
                hwndWindow = Win32Window(hwnd)
                # 获取窗口的区域
                left, top, right, bottom = hwndWindow.left, hwndWindow.top, hwndWindow.right, hwndWindow.bottom
                box = {"top": top + y, "left": left + x, "width": w, "height": h}

                image_sct = sct.grab(box)
                im_opencv = np.array(image_sct)
                #im_opencv = cv2.convertScaleAbs(im_opencv)
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        if types == 1:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)
        elif types == 2:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR)
        elif types == 3:
            return cv2.cvtColor(im_opencv, cv2.COLOR_BGR2HSV)
            # return cv2.cvtColor(im_opencv, cv2.COLOR_RGBA2RGB)


def pictureImg(hwnd: int, x: int, y: int, x1: int, y1: int,back:int):
    if back != 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
            hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
            saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
            saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
            saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap
            saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)  # 截取从左上角（0，0）长宽为（w，h）的图片
            signedIntsArray = saveBitMap.GetBitmapBits(True)
            im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
            im_opencv.shape = (h, w, 4)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        cv2.imwrite("C:/test_game/"+str(hwnd)+"hzend.png", cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR))
    elif back == 1:
        lock.acquire()
        w = x1 - x
        h = y1 - y
        try:
            with mss.mss() as sct:
                hwndWindow = Win32Window(hwnd)
                # 获取窗口的区域
                left, top, right, bottom = hwndWindow.left, hwndWindow.top, hwndWindow.right, hwndWindow.bottom
                box = {"top": top + y, "left": left + x, "width": w, "height": h}

                image_sct = sct.grab(box)
                im_opencv = np.array(image_sct)
        except Exception as e:
            logger.error(f"截图出错:{str(e)}，句柄:{hwnd},坐标：{x},{y},{x1},{y1}")
        finally:
            lock.release()
        cv2.imwrite("C:/test_game/"+str(hwnd)+"hzend.png", cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR))


def findColor(hwnd: int, lowerb:str,upperb:str, x: int, y: int, x1: int, y1: int, matching: int, back:int):
    returnStr = ""
    img_hsv = Window_Img(hwnd, x, y, x1, y1, 3, back)
    try:
        lowerbs = lowerb.split(",")
        upperbs = upperb.split(",")
        lowerbsUMat = (int(lowerbs[0]),int(lowerbs[1]),int(lowerbs[2]))
        upperbsUMat = (int(upperbs[0]),int(upperbs[1]),int(upperbs[2]))
        # 根据颜色阈值转换为二值化图像
        img_bin = cv2.inRange(img_hsv, lowerbsUMat, upperbsUMat)
        # 寻找轮廓（只寻找最外侧的色块）
        contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 设置最小面积阈值
        min_area = matching  # 根据实际情况调整

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
            returnStr = "yes"
        else:
            print("图片不符合要求")
    except Exception as e:
        logger.error(f"{hwnd}:识别场景图片出错:{str(e)}，,坐标：{x},{y},{x1},{y1}")
    finally:
        return returnStr


def FindPic(hwnd: int, cards, x: int, y: int, x1: int, y1: int, matching: float, type:int, back:int):
    #start_time = time.time()
    # cv2.imshow("source", source)
    # cv2.waitKey()
    #coordinate = []
    returnStr = ""
    try:
        if type == 2:
            source = Window_Img(hwnd, x, y, x1, y1,type,back)
        else:
            source = Window_Img(hwnd, x, y, x1, y1,1,back)
        count = 0
        if type == 1 or type == 2:
            for card in cards:
                count +=1
                #fileName = path + "\场景\\" + card
                if type == 2:
                    #cardGray = cv2.imdecode(np.fromfile(fileName, dtype=np.uint8), cv2.IMREAD_COLOR)
                    cardGray = 场景_dict.get(card)
                else:
                    #cardGray = cv2.imdecode(np.fromfile(fileName, dtype=np.uint8), 0)
                    cardGray = cv2.cvtColor(场景_dict.get(card), cv2.COLOR_BGR2GRAY)

                match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                locathions = np.where(match >= matching)
                if len(locathions[0]) == 0:
                    pass
                    #logger.info("未识别到：" + card)
                else:
                    temData = list(zip(*locathions[::-1]))[0]
                    intX = temData[0] + x
                    intY = temData[1] + y
                    intX = str(intX)
                    intY = str(intY)
                    returnStr = intX + "|" + intY+ "|" + str(count)
                    #logger.info("识别成功：" + returnStr)
                    #coordinate.append(intX)
                    #coordinate.append(intY)
                    break

        else:
            for card in cards:
                count += 1
                for cardGray in cards_dict_origin[card]:
                    match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match >= matching)
                    if len(locathions[0]) == 0:
                        pass
                        # logger.info("识别失败：" + card)
                    else:
                        temData = list(zip(*locathions[::-1]))[0]
                        intX = temData[0] + 393 + 29
                        intY = temData[1] + 510 + 40
                        intX = str(intX)
                        intY = str(intY)
                        returnStr = intX + "|" + intY + "|" + str(count)
                        #logger.info("识别成功：" + returnStr)
                        #coordinate.append(intX)
                        #coordinate.append(intY)
                        return returnStr

                '''h, w = cardGray.shape[0:2]
                for p in zip(*locathions[::-1]):
                    x1, y1 = p[0], p[1]
                    x2, y2 = x1 + w, y1 + h
                    cv2.rectangle(source, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.imshow("source2", source)
                cv2.waitKey()'''

        '''imgs = cv2.imread(sourceImg)
        cv2.imshow("source2", imgs)
        cv2.waitKey(0)'''

    except Exception as e:
        logger.error(f"{cards}:识别场景图片出错:{str(e)}，图片:{list(cards)},坐标：{x},{y},{x1},{y1}")
    finally:
        #end_time = time.time()
        #print("FindPic程序运行时间：%.2f秒" % (end_time - start_time))
        return returnStr

def FindPicRes(hwnd: int, cards, x: int, y: int, x1: int, y1: int, matching: float, type:int, back:int):
    #start_time = time.time()
    # cv2.imshow("source", source)
    # cv2.waitKey()
    #coordinate = []
    returnStr = ""
    try:
        if type == 2:
            source = Window_Img(hwnd, x, y, x1, y1,type,back)
        else:
            source = Window_Img(hwnd, x, y, x1, y1,1,back)
        count = 0
        if type == 1 or type == 2:
            for card in cards:
                count +=1
                #fileName = path + "\场景\\" + card
                if type == 2:
                    #cardGray = cv2.imdecode(np.fromfile(fileName, dtype=np.uint8), cv2.IMREAD_COLOR)
                    cardGray = 场景_dict.get(card)
                else:
                    #cardGray = cv2.imdecode(np.fromfile(fileName, dtype=np.uint8), 0)
                    cardGray = cv2.cvtColor(场景_dict.get(card), cv2.COLOR_BGR2GRAY)

                match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                locathions = np.where(match >= matching)
                if len(locathions[0]) == 0:
                    pass
                    #logger.info("未识别到：" + card)
                else:
                    aint = 2
                    for pt in zip(*locathions[::-1]):
                        if aint%2==0:
                            print(f"得到结果：{pt[0]+x},{pt[1]+y}")
                        aint = aint + 1
                    print("-----------------------------")
                    temData = list(zip(*locathions[::-1]))[0]
                    intX = temData[0] + x
                    intY = temData[1] + y
                    intX = str(intX)
                    intY = str(intY)
                    returnStr = intX + "|" + intY+ "|" + str(count)
                    #logger.info("识别成功：" + returnStr)
                    #coordinate.append(intX)
                    #coordinate.append(intY)
                    break

        else:
            for card in cards:
                count += 1
                for cardGray in cards_dict_origin[card]:
                    match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match >= matching)
                    if len(locathions[0]) == 0:
                        pass
                        # logger.info("识别失败：" + card)
                    else:
                        temData = list(zip(*locathions[::-1]))[0]
                        intX = temData[0] + 393 + 29
                        intY = temData[1] + 510 + 40
                        intX = str(intX)
                        intY = str(intY)
                        returnStr = intX + "|" + intY + "|" + str(count)
                        #logger.info("识别成功：" + returnStr)
                        #coordinate.append(intX)
                        #coordinate.append(intY)
                        return returnStr

                '''h, w = cardGray.shape[0:2]
                for p in zip(*locathions[::-1]):
                    x1, y1 = p[0], p[1]
                    x2, y2 = x1 + w, y1 + h
                    cv2.rectangle(source, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.imshow("source2", source)
                cv2.waitKey()'''

        '''imgs = cv2.imread(sourceImg)
        cv2.imshow("source2", imgs)
        cv2.waitKey(0)'''

    except Exception as e:
        logger.error(f"{cards}:识别场景图片出错:{str(e)}，图片:{list(cards)},坐标：{x},{y},{x1},{y1}")
    finally:
        #end_time = time.time()
        #print("FindPic程序运行时间：%.2f秒" % (end_time - start_time))
        return returnStr

balls = ["光精灵", "雷精灵", "木精灵", "魔精灵", "暗精灵", "彩精灵", "幻精灵", "土精灵","魂精灵","冰精灵"]
ballsDz = ["魔精灵", "暗精灵", "土精灵"]

def filter_numbers(s):
    return re.findall(r'\d+', s)

def is_number(value):
    pattern = r'^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$'
    return bool(re.match(pattern, str(value)))

def getOcrNum(res: dict,oldNumbers=0):
    if res["code"] == 100:
        score = 0
        levels = 0
        numbers = 0
        for line in res["data"]:
            score = round(line['score'], 2)
            levels = line['text']
            #logger.info(f"-置信度：{score}，文本：{levels}")
            if score >= 0.75:
                numbers = filter_numbers(levels)
                if(numbers.__len__()<=0):
                    break
                numbers = int(numbers[0])
                if is_number(numbers):

                    if oldNumbers <= 0:
                        if numbers > 0:
                            oldNumbers = numbers
                            #rint(f"当前关卡为：{oldNumbers}")
                            return numbers
                    elif(numbers > 0 and numbers >= oldNumbers and numbers <= (oldNumbers + 5)):
                        oldNumbers = numbers
                        #print(f"当前关卡为：{oldNumbers}")
                        return numbers
        return -1

    return -1
def getOcrTxt(res: dict,tager="",x=-1,y=-1):
    if res["code"] == 100:
        score = 0
        levels = 0
        numbers = 0
        for line in res["data"]:
            score = round(line['score'], 2)
            levels = line['text']
            #logger.info(f"-置信度：{score}，文本：{levels}")
            if score >= 0.75:
                if len(tager) > 0:
                    if tager in levels:
                        if x >= 0 and y >= 0:
                            retX = line['box'][0][0] + x
                            retY = line['box'][0][1] + y
                            returnStr = str(retX)+"|"+str(retY)+"|1"
                            return returnStr
                else:
                    return levels
        return ""

    return ""

def FindStr(hwnd: int, strs: str, x: int, y: int, x1: int, y1: int,back:int,ocr):
    result = ""
    try:
        sourceImg = Window_Img(hwnd, x, y, x1, y1, 1, back)
        retval, buffer = cv2.imencode('.png', sourceImg)
        imageBase64 = b64encode(buffer).decode('utf-8')
        res = ocr.runBase64(imageBase64)
        result = getOcrTxt(res,strs,x,y)
        return result
    except Exception as e:
        logger.error(f"识别FindStr出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        return result


def getOcr(hwnd: int, x: int, y: int, x1: int, y1: int,back:int,oldNum:int,ocr,isNum=0):
    result = ""
    try:
        sourceImg = Window_Img(hwnd, x, y, x1, y1, 1, back)
        retval, buffer = cv2.imencode('.png', sourceImg)
        imageBase64 = b64encode(buffer).decode('utf-8')
        res = ocr.runBase64(imageBase64)
        if(isNum ==1):
            numResult = getOcrNum(res, oldNum)
            if(numResult):
                result = str(numResult)
        else:
            result = getOcrTxt(res)
        return result
    except Exception as e:
        logger.error(f"识别getOcr出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        return result



def FindPicS(hwnd: int, cards, x: int, y: int, x1: int, y1: int, matching: float,tag:int,recursion:int,back:int):
    #start_time = time.time()
    results = []
    try:
        source = Window_Img(hwnd, x, y, x1, y1,1,back)
        if tag > 0:
            lock3.acquire()
            try:
                results = getResultMatchTemplate(source,cards,tag,matching,x,y)
                return results
            finally:
                lock3.release()

        else:
            for card in cards:
                if len(results) >= 3:
                    # logger.info("已识别到3个英雄，退出循环")
                    return results
                cardsOrigin = cards_dict_origin[card]
                for cardGray in cardsOrigin:
                    match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                    locathions = np.where(match >= matching)
                    if len(locathions[0]) == 0:
                        pass
                    else:
                        temData = list(zip(*locathions[::-1]))[0]
                        intX = temData[0] + x + 29
                        intY = temData[1] + y + 40
                        # restr = {card:[intX,intY]}
                        restr = card + "," + str(intX) + "," + str(intY)
                        # logger.info(f"{fileName}----识别成功:{card}")
                        results.append(restr)
                        break


                    '''h, w = cardGray.shape[0:2]
                    for p in zip(*locathions[::-1]):
                        x1, y1 = p[0], p[1]
                        x2, y2 = x1 + w, y1 + h
                        cv2.rectangle(source, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
                    cv2.imshow("source2", source)
                    cv2.waitKey()'''
            '''imgs = cv2.imread(sourceImg)
            cv2.imshow("source2", imgs)
            cv2.waitKey(0)'''
            # end_time = time.time()
            # print("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
        if recursion > 0:
            if len(results) >= 3:
                # logger.info("已识别到3个英雄，退出循环")
                return results
            else:
                time.sleep(0.05)
                #递归
                #logger.info(f"递归调用次数：{recursion}")
                FindPicS(hwnd, cards, x, y, x1, y1, matching, tag, recursion-1,back)
        else:
            return results

    except Exception as e:
        logger.error(f"识别所有英雄出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        infoCard(cards)
        logger.error(f"识别所有英雄出错，进行英雄初始化:{cards},坐标：{x},{y},{x1},{y1}")

    finally:
        #end_time = time.time()
        #logger.info("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
        return results
def threadHadler(image_pairs,source,type):
    return [pool.submit(imgMacthOldPool, cardName, source,type) for cardName in image_pairs]



def FindPicSBy对战(hwnd: int, cards, cardsAll, x: int, y: int, x1: int, y1: int, matching: float, tag: int,
                 recursion: int, back: int):
    #start_time = time.time()
    try:
        results = []
        #构造多线程要执行的卡牌
        image_pairs = []
        for cardName in cards:
            image_pairs.append((cardName))

        for recursion in range(recursion):
            results = []
            results = FindPicS(hwnd, cards, x, y, x1, y1, matching, 0, 0, back)
            if len(results) == 3:
                logger.info("已识别到3个英雄，退出循环")
                return results
            else:
                results = []
            source = Window_Img(hwnd, x, y, x1, y1, 1, back)
            futures = threadHadler(image_pairs,source,1)
            for future in futures:
                res = future.result()
                print(f"Image pair:: {res}")
                if len(res) > 0:
                    results.append(res)
            if len(results) == 3:
                logger.info("futures已识别到3个英雄，退出循环")
                return results
            else:
                print("识别到部分")
                    #results = []
            #time.sleep(0.05)
            # logger.info(f"递归次数:{recursion}")
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"test识别所有英雄出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        logger.error(f"test识别所有英雄出错，进行英雄初始化:{cards},坐标：{x},{y},{x1},{y1}")
        infoCard(cards)
    finally:
        #end_time = time.time()
        #logger.info("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
        '''if len(results) > 0:
            timestamp = int(time.time())
            random_number = str(random.randint(0, 10000000))
            sourceImg = str(timestamp) + random_number + ".tif"
            cv2.imwrite(sourceImg,source)
            cv2.imencode('.tif', source)[1].tofile(results[0].split(",")[0]+sourceImg)
            leftClick(hwnd, 722, 572)'''
        return results
def FindPicSBy合作(hwnd: int, cards, cardsAll, x: int, y: int, x1: int, y1: int, matching: float, tag: int,
                 recursion: int, back: int):
    #start_time = time.time()
    try:
        results = []
        #构造多线程要执行的卡牌
        image_pairs = []
        for cardName in cards:
            image_pairs.append((cardName))

        for recursion in range(recursion):
            results = FindPicS(hwnd, cardsAll, x, y, x1, y1, matching, 0, 0, back)
            if len(results) == 3:
                logger.info("已识别到3个英雄，退出循环")
                return results
            else:
                results = []

            source = Window_Img(hwnd, x, y, x1, y1, 1, back)
            futures = threadHadler(image_pairs,source,2)
            for future in futures:
                res = future.result()
                print(f"Image pair:: {res}")
                if len(res) > 0:
                    results.append(res)
            if len(results) > 0:
                logger.info("futures已识别到3个英雄，退出循环")
                return results
            else:
                print("识别到部分")
                    #results = []
            #time.sleep(0.05)
            # logger.info(f"递归次数:{recursion}")
            results = []
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"test识别所有英雄出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        logger.error(f"test识别所有英雄出错，进行英雄初始化:{cards},坐标：{x},{y},{x1},{y1}")
        infoCard(cards)
    finally:
        #end_time = time.time()
        #logger.info("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
        '''if len(results) > 0:
            timestamp = int(time.time())
            random_number = str(random.randint(0, 10000000))
            sourceImg = str(timestamp) + random_number + ".tif"
            cv2.imwrite(sourceImg,source)
            cv2.imencode('.tif', source)[1].tofile(results[0].split(",")[0]+sourceImg)
            leftClick(hwnd, 722, 572)'''
        return results

def FindPicSTest(hwnd: int, cards,cardsAll, x: int, y: int, x1: int, y1: int, matching: float, tag: int, recursion: int,back:int):
    #start_time = time.time()
    try:
        results = []
        for recursion in range(recursion):
            results = []
            source = Window_Img(hwnd, x, y, x1, y1,1,back)
            for i in range(2):
                if i == 0:
                    tag = 1
                else:
                    tag = 0
                if tag == 1:
                    for card in cards:
                        cardsOrigin = cards_dict_originAll[card]
                        flag = False
                        for cardGray in cardsOrigin:
                            match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                            locathions = np.where(match >= 0.87)
                            if len(locathions[0]) == 0:
                                pass
                            else:
                                if card in balls:
                                    #logger.info("精灵特征验证：" + card)
                                    sourceequ = cv2.equalizeHist(source)
                                    for cardGraya in cards_dict[card]:
                                        res = imgMacthOld(cardGraya, sourceequ,0.69,5)
                                        if res > 0:
                                            break
                                        #else:
                                            #flag = True
                                            #break
                                else:
                                    #logger.info("其它特征验证："+card)
                                    sourceequ = cv2.equalizeHist(source)
                                    cardGrayqu = cv2.equalizeHist(cardGray)
                                    res = imgMacthOld(cardGrayqu, sourceequ)
                                    if res == 0:
                                        #logger.info("检测到当前卡牌集不存在，结束循环,减少无用的检测")
                                        break


                                if res > 0:
                                    # logger.info("特征验证成功：" + card)
                                    xa = 0
                                    ya = 0
                                    if res == 1:
                                        xa = 434
                                        ya = 560
                                    elif res == 2:
                                        xa = 518
                                        ya = 570
                                    elif res == 3:
                                        xa = 601
                                        ya = 561

                                    restr = card + "," + str(xa) + "," + str(ya)
                                    results.append(restr)
                                    return results
                            if flag:
                                #logger.info("flag检测到当前卡牌集不存在，结束循环")
                                break
                else:
                    for card in cardsAll:
                        if len(results) >= 3:
                            # logger.info("已识别到3个英雄，退出循环")
                            return results
                        cardsOrigin = cards_dict_origin[card]
                        for cardGray in cardsOrigin:
                            match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
                            locathions = np.where(match >= matching)
                            if len(locathions[0]) == 0:
                                pass
                            else:
                                temData = list(zip(*locathions[::-1]))[0]
                                intX = temData[0] + x + 29
                                intY = temData[1] + y + 40
                                # restr = {card:[intX,intY]}
                                restr = card + "," + str(intX) + "," + str(intY)
                                # logger.info(f"{fileName}----识别成功:{card}")
                                results.append(restr)
                                break

                            '''h, w = cardGray.shape[0:2]
                            for p in zip(*locathions[::-1]):
                                x1, y1 = p[0], p[1]
                                x2, y2 = x1 + w, y1 + h
                                cv2.rectangle(source, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
                            cv2.imshow("source2", source)
                            cv2.waitKey()'''
                    '''imgs = cv2.imread(sourceImg)
                    cv2.imshow("source2", imgs)
                    cv2.waitKey(0)'''
                    # end_time = time.time()
                    # print("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
                    if len(results) >= 3:
                        # logger.info("已识别到3个英雄，退出循环")
                        return results
                    if len(results) <= 2:
                        #logger.info("10次循环只得到一个值，则清空")
                        results =[]
            time.sleep(0.05)
            #logger.info(f"递归次数:{recursion}")
    except Exception as e:
        logger.error(f"test识别所有英雄出错:{str(e)},坐标：{x},{y},{x1},{y1}")
        logger.error(f"test识别所有英雄出错，进行英雄初始化:{cards},坐标：{x},{y},{x1},{y1}")
        infoCard(cards)
    finally:
        #end_time = time.time()
        #logger.info("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))
        '''if len(results) > 0:
            timestamp = int(time.time())
            random_number = str(random.randint(0, 10000000))
            sourceImg = str(timestamp) + random_number + ".tif"
            cv2.imwrite(sourceImg,source)
            cv2.imencode('.tif', source)[1].tofile(results[0].split(",")[0]+sourceImg)
            leftClick(hwnd, 722, 572)'''
        return results


'''def FindStr(hwnd: int, strs: str, x: int, y: int, x1: int, y1: int):
    result = ""
    try:
        sourceImg = Window_Img(hwnd, x, y, x1, y1, 0)
        box_list = detect_model.detect(sourceImg)
        if len(box_list) > 0:
            for point in box_list:
                point = detect_model.order_points_clockwise(point)
                textimg = detect_model.get_rotate_crop_image(sourceImg, point.astype(np.float32))
                angle = angle_model.predict(textimg)
                if angle == '180':
                    textimg = cv2.rotate(textimg, 1)
                result = rec_model.predict_text(textimg)
                if len(result) > 0:
                    if strs in result:
                        result = strs
                        return result
                    break
        return result
    except Exception as e:
        logger.error(f"识别getOcr出错:{str(e)}")
        return result

def getOcr(hwnd: int, x: int, y: int, x1: int, y1: int, tag: int):
    result = ""
    try:
        sourceImg = Window_Img(hwnd, x, y, x1, y1,0)
        box_list = detect_model.detect(sourceImg)
        if len(box_list) > 0:
            for point in box_list:
                point = detect_model.order_points_clockwise(point)
                textimg = detect_model.get_rotate_crop_image(sourceImg, point.astype(np.float32))
                angle = angle_model.predict(textimg)
                if angle == '180':
                    textimg = cv2.rotate(textimg, 1)
                result = rec_model.predict_text(textimg)
                if len(result) > 0:
                    if tag == 1:
                        pattern = r'\d+'
                        results = findall(pattern, result)
                        if len(results) > 0:
                            result = results[0]
                    break
        return result
    except Exception as e:
        logger.error(f"识别getOcr出错:{str(e)}")
        return result'''

'''def FindStr(hwnd: int, strs: str, x: int, y: int, x1: int, y1: int):
    #start_time = time.time()
    results = ""
    try:
        resultStr = shareData.plugin.detectRectText(hwnd, x, y, x1 - x, y1 - y)
        #end_time = time.time()
        #print("FindStr程序运行时间：%.2f秒" % (end_time - start_time))
        if len(resultStr) < 3:
            return results
        else:
            jsonObj = json.loads(resultStr)
            for key in jsonObj:
                if strs in key:
                    value = jsonObj[key]
                    # results.append(x + value[0])
                    # results.append(y + value[1])
                    intX = x + value[0]
                    intY = y + value[1]
                    results = str(intX) + "|" + str(intY)
                    break
            #logger.info("FindStr识别结果：" + results)
            return results
    except Exception as e:
        logger.error(f"识别FindStr出错:{str(e)}")
        return results
    finally:
        return results



def getOcr(hwnd: int, x: int, y: int, x1: int, y1: int, tag: int):
    #start_time = time.time()
    result = ""
    try:
        resultStr = shareData.plugin.detectRectText(hwnd, x, y, x1 - x, y1 - y)
        #end_time = time.time()
        #print("getOcr程序运行时间：%.2f秒" % (end_time - start_time))
        if len(resultStr) < 3:
            return ""
        else:
            result = ""
            jsonObj = json.loads(resultStr)
            for key in jsonObj:
                result = key
                break
            if tag == 1 and len(result) > 0:
                pattern = r'\d+'
                result = findall(pattern, result)[0]
            #logger.info("getOcr识别结果："+result)
            return result
    except Exception as e:
        logger.error(f"识别getOcr出错:{str(e)}")
        return result
    finally:
        return result'''
# --点击方法--
def leftClick(wnd: int, x: int, y: int):
    # 模拟鼠标指针， 传送到指定坐标
    long_position = win32api.MAKELONG(x, y)
    # 模拟鼠标按下
    win32api.SendMessage(wnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
    time.sleep(0.04)
    # 模拟鼠标抬起
    win32api.SendMessage(wnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)

def dmGetCircle(hwnd:int,position,recursion,back):
    start_time = time.time()
    returnStr = ""
    #新  5,144,397,555,宽高(392,411)
    try:
        #21,105,400,554
        x = 4
        y = 103
        x1 = 414
        y1 = 582
        for recursion in range(recursion):
            img = Window_Img(hwnd, x, y, x1, y1, 3,back)
            returnStr = getCircle(img,position)
            if len(returnStr) > 0:
                return returnStr
            cards =["船长喊话.bmp"]
            findPicRes = FindPic(hwnd, cards, 752, 144, 791,215, 0.82, 1,back)
            if len(findPicRes) > 0:
                returnStr = "10"
                logger.info("检测到船长喊话")
                return returnStr
            logger.info(f"没检测到继续循环检测:{recursion}")
            time.sleep(0.04)
    except Exception as e:
        logger.error(f"识别寒冰船长出错:{str(e)},,坐标：{x},{y},{x1},{y1}")
    finally:
        end_time = time.time()
        print("识别寒冰船长时间：%.2f秒" % (end_time - start_time))
        return returnStr


cards_dict = {}
cards_dict_origin = {}
cards_dict_originAll = {}
所有卡牌提前预处理 = {}
def infoCard(cards):
    if p3 is None:
        卡牌位置初始化()
    if len(cards) > 0:
        clahe = cv2.createCLAHE(clipLimit=7, tileGridSize=(8, 8))
        for card in cards:
            try:
                if card not in cards_dict:
                    cardImgs = []
                    cardImgsorigin = []
                    cardImgsoriginAll = []
                    卡牌提前预处理数组 = []
                    for i in range(2):
                        if i == 1:
                            fileName = path + "\快速手牌\\" + card
                        elif i ==0:
                            fileName = path + "\手牌\\" + card

                        listdirs = os.listdir(fileName)
                        for file in listdirs:
                            cardGray = cv2.imdecode(np.fromfile(fileName + '\\' + file, dtype=np.uint8), 0)
                            cardImgsoriginAll.append(cardGray)
                            equalizeHistImg = cv2.equalizeHist(cardGray)
                            claheImg = clahe.apply(equalizeHistImg)
                            卡牌提前预处理数组.append(claheImg)
                            if i == 0:
                                cardImgsorigin.append(cardGray)
                                cardImgs.append(cv2.equalizeHist(cardGray))

                    if len(cardImgs) > 0:
                        cards_dict[card] = cardImgs
                        logger.info(f"cardImgs{card}:初始化完成")
                    if len(cardImgsorigin) > 0:
                        cards_dict_origin[card] = cardImgsorigin
                        logger.info(f"cardImgsorigin{card}:初始化完成")
                    if len(cardImgsoriginAll) > 0:
                        cards_dict_originAll[card] = cardImgsoriginAll
                        logger.info(f"cardImgsoriginAll{card}:初始化完成")
                    if len(卡牌提前预处理数组) > 0:
                        所有卡牌提前预处理[card] = 卡牌提前预处理数组
                        logger.info(f"所有卡牌提前预处理{card}:初始化完成")
            except Exception as e:
                logger.error(f"{card}:英雄初始化失败:{str(e)}")
my_kpList = ["魔"]
def getAllKpName():
    fileName = path + "\手牌\\"
    listdirs = os.listdir(fileName)
    for kpName in listdirs:
        if kpName not in my_kpList:
            my_kpList.append(kpName)

def getKpName(cardName):
    if cardName in my_kpList:
        print(f"'{cardName}' 在列表中")
        return cardName
    else:
        print(f"'{cardName}' 不在列表中")
        return ""


场景_dict = {}
def info场景():
    if len(场景_dict) > 0:
        return
    #加载卡牌名称
    getAllKpName()

    fileName = path + "\场景\\"
    listdirs = os.listdir(fileName)
    for file in listdirs:
        场景Gray = cv2.imdecode(np.fromfile(fileName + '\\' + file, dtype=np.uint8),cv2.IMREAD_COLOR)
        try:
            if 场景_dict.get(file) == None:
                场景_dict[file] = 场景Gray
                print(f"加载图片：{file}")
        except Exception as e:
            logger.error(f"{file}：场景初始化失败:{str(e)}")




#直方图均衡化
def imgHandle(image):
    # 图片转为灰度图
    #image = cv2.imread(imgsr, cv2.IMREAD_GRAYSCALE)
    rows, cols = image.shape
    # 计算灰度直方图
    grayHist = calcGrayHist(image)
    # 计算累加灰度直方图
    zeroCumuMoment = np.zeros([256], np.uint32)
    for p in range(256):
        if p == 0:
            zeroCumuMoment[p] = grayHist[0]
        else:
            zeroCumuMoment[p] = zeroCumuMoment[p - 1] + grayHist[p]
    # 根据累加的灰度直方图得到输入与输出灰度级之间的映射关系
    output = np.zeros([256], np.uint8)
    cofficient = 256.0 / (rows * cols)
    for p in range(256):
        q = cofficient * float(zeroCumuMoment[p]) - 1
        if q >= 0:
            output[p] = np.math.floor(q)
        else:
            output[p] = 0
    # 得出均衡化图像
    equalHistimg = np.zeros(image.shape, np.uint8)
    for r in range(rows):
        for c in range(cols):
            equalHistimg[r][c] = output[image[r][c]]
    return equalHistimg

#计算灰度直方图
def calcGrayHist(image):
    rows,clos = image.shape
    #创建一个矩阵用于存储灰度值
    grahHist = np.zeros([256],np.uint64)
    #print('这是初始化矩阵')
    #print(grahHist )
    for r in range(rows):
        for c in range(clos):
            #通过图像矩阵的遍历来将灰度值信息放入我们定义的矩阵中
            grahHist[image[r][c]] +=1
    return grahHist

#图片匹配
def imgMacthOldPool(cardName,sourceImg,type,sim=0.57,matchCount=6):
    sourceImgNew = cv2.equalizeHist(sourceImg)
    clahe = cv2.createCLAHE(clipLimit=7, tileGridSize=(8, 8))
    sourceImgNew = clahe.apply(sourceImgNew)

    sift = cv2.SIFT_create(nfeatures=350)
    预处理的卡牌s = 所有卡牌提前预处理[cardName]
    没处理的卡牌s = cards_dict_originAll[cardName]
    for index, tagImg in enumerate(没处理的卡牌s, start=0):
        match = cv2.matchTemplate(sourceImg, tagImg, cv2.TM_CCOEFF_NORMED)
        locathions = np.where(match >= 0.86)
        if len(locathions[0]) == 0:
            pass
        else:
            tagImg = 预处理的卡牌s[index]
            if type == 1:
                if cardName in ballsDz:
                    sim = 0.74
                    matchCount = 5
            # tagImg = cv2.equalizeHist(tagImg)
            # tagImg = clahe.apply(tagImg)

            # cv2.imshow(cardName, tagImg)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            #
            # cv2.imshow(cardName+"sourceImgNew", sourceImgNew)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()


            MIN_MATCH_COUNT = matchCount  # 设置最低特征点匹配数量为10
            # 使用SIFT查找关键点和描述符

            kp1, des1 = sift.detectAndCompute(tagImg, None)
            kp2, des2 = sift.detectAndCompute(sourceImgNew, None)
            # 创建设置FLANN匹配
            # FLANN_INDEX_KDTREE = 0
            # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            # search_params = dict(checks=50)
            # flann = cv2.FlannBasedMatcher(index_params, search_params)
            # matches = flann.knnMatch(des1, des2, k=2)

            # 暴力匹配器
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)

            #得到匹配特征点坐标
            destination = []
            good = []
            count = 0
            for m, n in matches:
                if m.distance < sim * n.distance:  # 舍弃大于0.7的匹配
                    count += 1
                    good.append(m)
                    pt2 = kp2[m.trainIdx].pt
                    x = int(pt2[0]) + 385
                    y = int(pt2[1]) + 511
                    destination.append(str(x) + ":" + str(y))  # 得到目标图的坐标
                    if count >= MIN_MATCH_COUNT:
                        break

            if len(good) >= MIN_MATCH_COUNT:
                res = 卡牌位置判断(destination,(MIN_MATCH_COUNT-1))
                if res > 0:
                    xa = 0
                    ya = 0
                    if res == 1:
                        xa = 434
                        ya = 560
                    elif res == 2:
                        xa = 518
                        ya = 570
                    elif res == 3:
                        xa = 601
                        ya = 561
                restr = cardName + "," + str(xa) + "," + str(ya)
                return restr
    return ""
#图片匹配
def imgMacthOld(tagImg,sourceImg,sim=0.67,matchCount=10):
    tagImg = cv2.equalizeHist(tagImg)
    tag = 1
    if tag == 1:
        clahe = cv2.createCLAHE(clipLimit=7, tileGridSize=(8, 8))
        tagImg = clahe.apply(tagImg)

    sourceImg = cv2.equalizeHist(sourceImg)
    if tag == 1:
        sourceImg = clahe.apply(sourceImg)


    MIN_MATCH_COUNT = matchCount  # 设置最低特征点匹配数量为10
    # 使用SIFT查找关键点和描述符
    sift = cv2.SIFT_create(nfeatures=400)
    kp1, des1 = sift.detectAndCompute(tagImg, None)
    kp2, des2 = sift.detectAndCompute(sourceImg, None)
    # 创建设置FLANN匹配
    # FLANN_INDEX_KDTREE = 0
    # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # search_params = dict(checks=50)
    # flann = cv2.FlannBasedMatcher(index_params, search_params)
    # matches = flann.knnMatch(des1, des2, k=2)

    # 暴力匹配器
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    #得到匹配特征点坐标
    destination = []
    good = []
    count = 0
    for m, n in matches:
        if m.distance < sim * n.distance:  # 舍弃大于0.7的匹配
            count += 1
            good.append(m)
            pt2 = kp2[m.trainIdx].pt
            x = int(pt2[0]) + 385
            y = int(pt2[1]) + 511
            destination.append(str(x) + ":" + str(y))  # 得到目标图的坐标
            if count >= MIN_MATCH_COUNT:
                break

    if len(good) >= MIN_MATCH_COUNT:
        return 卡牌位置判断(destination,(MIN_MATCH_COUNT-1))
    else:
        return 0

p1 =None
p2 =None
p3 =None
def 卡牌位置初始化():
    logger.info("英雄区域坐标初始化")
    global p1
    global p2
    global p3
    x1 = 392
    y1 = 510
    w1 = 81
    h1 = 104
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试

    p1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w2 = 79
    h2 = 103
    x2 = 479
    y2 = 511
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p2 = Path([(x2, h2 + y2), (x2, y2), (x2 + w2, y2), (x2 + w2, y2 + h2)])

    w3 = 81
    h3 = 100
    x3 = 565
    y3 = 512
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p3 = Path([(x3, h3 + y3), (x3, y3), (x3 + w3, y3), (x3 + w3, y3 + h3)])

def 卡牌位置判断(zbs,ci):
    if p3 is None:
        卡牌位置初始化()
    i1 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        a = p1.contains_point((x, y))
        if a:
            i1 += 1
        if i1 >= ci:
            return 1

    i2 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        # print(f"{x},{y}")
        a = p2.contains_point((x, y))
        if a:
            i2 += 1
        if i2 >= ci:
            return 2


    i3 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        a = p3.contains_point((x, y))
        if a:
            i3 += 1
        if i3 >= ci:
            return 3

    return 0


def getResultMatchTemplate(source,cards,tag,matching,x,y):
    cardQueue.queue.clear()
    count = 0
    results = []
    for card in cards:
        if tag == 1:
            cardsOrigin = cards_dict_originAll[card]
            for cardGray in cardsOrigin:
                pool.submit(matchTemplate, source, cardGray, card, matching, x, y)
                count += 1

            cardsOrigin = cards_dict_origin[card]
            for cardGray in cardsOrigin:
                pool.submit(matchTemplate, source, cardGray, card,0.85, x, y)
                count += 1
        elif tag == 2:
            cardsOrigin = cards_dict_origin[card]
            for cardGray in cardsOrigin:
                pool.submit(matchTemplate,source,cardGray,card,matching,x,y)
                count +=1

    while count > 0:
        res = cardQueue.get()
        if len(res) > 0:
            count -=1
            if res not in "none":
                if tag == 1:
                    results.append(res)
                    return results
                elif tag == 2:
                    results.append(res)
                    if len(results) >=3:
                        return results
    return results

def matchTemplate(source,cardGray,card,matching,x,y):
    match = cv2.matchTemplate(source, cardGray, cv2.TM_CCOEFF_NORMED)
    locathions = np.where(match >= matching)
    if len(locathions[0]) == 0:
        cardQueue.put("none")
    else:
        temData = list(zip(*locathions[::-1]))[0]
        intX = temData[0] + x + 29
        intY = temData[1] + y + 40
        restr = card + "," + str(intX) + "," + str(intY)
        cardQueue.put(restr)




