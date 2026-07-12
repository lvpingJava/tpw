import json
from flask import Flask
from flask import request
import DmTool
from WxAuToTool import WxAuToTool
import threading
from queue import Queue
import webbrowser
import pythoncom
from log import Log
loggerserver = Log().get_log()
import os
import re
from matplotlibes.matp_api import OcrAPI
webAppServer = Flask(__name__)


def is_number(value):
    pattern = r'^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$'
    return bool(re.match(pattern, str(value)))

@webAppServer.route('/test', methods=['POST','get'])
def test():
    webbrowser.open("http://www.baidu.com")
    return "haha"

@webAppServer.route('/openUrl', methods=['POST'])
def openUrl():
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        tag =int(getData['tag'])
        if tag == 1:
            webbrowser.open("https://www.yuque.com/lufei-ou5am/ak0ekx/xqhzbnt8c5klprlr?singleDoc# 《阵容说明》")
    return ""

@webAppServer.route('/cardInfo', methods=['POST'])
def cardInfo():
        requestStr = request.data.decode("utf-8")
        if len(requestStr) > 0:
            getData = json.loads(requestStr)
            cardStr = getData['cards']
            cards = cardStr.split("|")
            cards=list(filter(None, cards))
            DmTool.infoCard(cards)
        return ""


@webAppServer.route('/findPicTest', methods=['POST'])
def findPicTest():
        resultStr = ""
        requestStr = request.data.decode("utf-8")
        if len(requestStr) > 0:
            getData = json.loads(requestStr)
            hwnd = getData['hwnd']
            if hwnd > 0:
                #print(f"游戏句柄={hwnd}")
                cardStr = getData['cards']
                cards = cardStr.split("|")
                cards=list(filter(None, cards))

                cardAllStr = getData['cardsAll']
                cardAlls = cardAllStr.split("|")
                cardsAll = list(filter(None, cardAlls))

                regionSr = getData['region']
                regions = regionSr.split(",")
                matching=float(getData['matching'])
                tag = getData['tag']
                recursion = getData['recursion']
                back = getData['back']
                result = findPicTesto(hwnd, cards,cardsAll, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),matching,int(tag),int(recursion),int(back))
                resultStr = '|'.join(result)
        return resultStr

@webAppServer.route('/findPics', methods=['POST'])
def findPics():
        resultStr = ""
        requestStr = request.data.decode("utf-8")
        if len(requestStr) > 0:
            getData = json.loads(requestStr)
            hwnd = getData['hwnd']
            if hwnd > 0:
                #print(f"游戏句柄={hwnd}")
                cardStr = getData['cards']
                cards = cardStr.split("|")
                cards=list(filter(None, cards))
                regionSr = getData['region']
                regions = regionSr.split(",")
                matching=float(getData['matching'])
                tag = getData['tag']
                recursion = getData['recursion']
                back = getData['back']
                result = getPicsData(hwnd, cards, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),matching,int(tag),int(recursion),int(back))
                resultStr = '|'.join(result)
        return resultStr

@webAppServer.route('/findPicsByDZ', methods=['POST'])
def findPicsByDZ():
        resultStr = ""
        requestStr = request.data.decode("utf-8")
        if len(requestStr) > 0:
            getData = json.loads(requestStr)
            hwnd = getData['hwnd']
            if hwnd > 0:
                # print(f"游戏句柄={hwnd}")
                cardStr = getData['cards']
                cards = cardStr.split("|")
                cards = list(filter(None, cards))

                cardAllStr = getData['cardsAll']
                cardAlls = cardAllStr.split("|")
                cardsAll = list(filter(None, cardAlls))

                regionSr = getData['region']
                regions = regionSr.split(",")
                matching = float(getData['matching'])
                tag = getData['tag']
                recursion = getData['recursion']
                back = getData['back']
                result = findPicTestoDz(hwnd, cards, cardsAll, int(regions[0]), int(regions[1]), int(regions[2]),
                                      int(regions[3]), matching, int(tag), int(recursion), int(back))
                resultStr = '|'.join(result)
        return resultStr

@webAppServer.route('/findPicsByHZ', methods=['POST'])
def findPicsByHZ():
        resultStr = ""
        requestStr = request.data.decode("utf-8")
        if len(requestStr) > 0:
            getData = json.loads(requestStr)
            hwnd = getData['hwnd']
            if hwnd > 0:
                # print(f"游戏句柄={hwnd}")
                cardStr = getData['cards']
                cards = cardStr.split("|")
                cards = list(filter(None, cards))

                cardAllStr = getData['cardsAll']
                cardAlls = cardAllStr.split("|")
                cardsAll = list(filter(None, cardAlls))

                regionSr = getData['region']
                regions = regionSr.split(",")
                matching = float(getData['matching'])
                tag = getData['tag']
                recursion = getData['recursion']
                back = getData['back']
                result = findPicTestoHz(hwnd, cards, cardsAll, int(regions[0]), int(regions[1]), int(regions[2]),
                                      int(regions[3]), matching, int(tag), int(recursion), int(back))
                resultStr = '|'.join(result)
        return resultStr


@webAppServer.route('/findPic', methods=['POST'])
def fidPic():
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            #print(f"游戏句柄={hwnd}")
            cardStr = getData['card']
            cards = cardStr.split("|")
            cards = list(filter(None, cards))
            regionSr = getData['region']
            regions = regionSr.split(",")
            matching = float(getData['matching'])
            tag = getData['tag']
            back = getData['back']
            resultStr = getPicData(hwnd, cards, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),matching,int(tag),int(back))
            #resultStr = '|'.join(result)
    return resultStr

@webAppServer.route('/findPicRes', methods=['POST'])
def findPicRes():
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            #print(f"游戏句柄={hwnd}")
            cardStr = getData['card']
            cards = cardStr.split("|")
            cards = list(filter(None, cards))
            regionSr = getData['region']
            regions = regionSr.split(",")
            matching = float(getData['matching'])
            tag = getData['tag']
            back = getData['back']
            resultStr = getPicDataRes(hwnd, cards, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),matching,int(tag),int(back))
            #resultStr = '|'.join(result)
    return resultStr

@webAppServer.route('/getCircle', methods=['POST'])
def getCircle():
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            position = getData['position']
            print("position:"+str(position))
            recursion = getData['recursion']
            back = getData['back']
            resultStr =DmTool.dmGetCircle(hwnd, position,int(recursion),int(back))
    return resultStr

@webAppServer.route('/findStr', methods=['POST'])
def findStr():
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            nameStr = getData['name']
            regionSr = getData['region']
            regions = regionSr.split(",")
            back = getData['back']
            resultStr = getStr(hwnd, nameStr, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),int(back))
    return resultStr

@webAppServer.route('/findColor', methods=['POST'])
def findColor():
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            lowerb = getData['lowerb']
            upperb = getData['upperb']
            matching = int(getData['matching'])
            regionSr = getData['region']
            regions = regionSr.split(",")
            back = getData['back']
            resultStr = DmTool.findColor(hwnd, lowerb, upperb,  int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]), matching, back)
    return resultStr

@webAppServer.route('/getOcr', methods=['POST'])
def ocr():
    isNumTag = 0
    resultStr = ""
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            #print(f"游戏句柄={hwnd}")
            regionSr = getData['region']
            oldNum = getData['oldNum']
            isNum = getData['isNum']
            if (is_number(oldNum)==False):
                oldNum = "0"
            regions = regionSr.split(",")
            back = getData['back']

            #判断卡牌名称是否存在
            if isNum == 100:
                isNumTag = 100
                isNum = 0

            resultStr = getOcr(hwnd, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),int(back),int(oldNum),int(isNum))
            print(f"识别到ocr:{resultStr}")
            # 判断卡牌名称是否存在
            if isNumTag == 100:
                result = DmTool.getKpName(resultStr)
                return result;
            else:
                return resultStr
    return resultStr

@webAppServer.route('/pictureImg', methods=['POST'])
def pictureImg():
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            #print(f"游戏句柄={hwnd}")
            regionSr = getData['position']
            regions = regionSr.split(",")
            back = getData['back']
            DmTool.pictureImg(hwnd, int(regions[0]), int(regions[1]), int(regions[2]), int(regions[3]),int(back))


@webAppServer.route('/getIslogin', methods=['POST'])
def getIslogin():
    if len(loginInfo) > 0:
        DmTool.info场景()
        return loginInfo
    else:
        return ""

def getPicsData(hwnd:int,cards,x: int, y: int, x1: int, y1: int,matching:float,tag: int,recursion:int,back:int):
    res = DmTool.FindPicS(hwnd, cards, x, y, x1, y1,matching,tag,recursion,back)
    return res

def findPicTesto(hwnd:int,cards,cardsAll,x: int, y: int, x1: int, y1: int,matching:float,tag: int,recursion:int,back:int):
    res = DmTool.FindPicSTest(hwnd,cards, cardsAll, x, y, x1, y1,matching,tag,recursion,back)
    return res
def findPicTestoDz(hwnd:int,cards,cardsAll,x: int, y: int, x1: int, y1: int,matching:float,tag: int,recursion:int,back:int):
    res = DmTool.FindPicSBy对战(hwnd,cards, cardsAll, x, y, x1, y1,matching,tag,recursion,back)
    return res

def findPicTestoHz(hwnd:int,cards,cardsAll,x: int, y: int, x1: int, y1: int,matching:float,tag: int,recursion:int,back:int):
    res = DmTool.FindPicSBy合作(hwnd,cards, cardsAll, x, y, x1, y1,matching,tag,recursion,back)
    return res

def getPicData(hwnd:int,cards,x: int, y: int, x1: int, y1: int,matching:float,tag:int,back:int):
    res = DmTool.FindPic(hwnd, cards, x, y, x1, y1,matching,tag,back)
    return res

def getPicDataRes(hwnd:int,cards,x: int, y: int, x1: int, y1: int,matching:float,tag:int,back:int):
    res = DmTool.FindPicRes(hwnd, cards, x, y, x1, y1,matching,tag,back)
    return res

def getOcr(hwnd:int,x: int, y: int, x1: int, y1: int,back:int,oldNum:int,isNum:int):
    res = DmTool.getOcr(hwnd, x, y, x1, y1,back,oldNum,ocr,isNum)
    return res

def getStr(hwnd:int,name:str,x: int, y: int, x1: int, y1: int,back:int):
    res = DmTool.FindStr(hwnd, name, x, y, x1, y1,back,ocr)
    return res

def webAppServerStart(params,port):
    global loginInfo,ocr
    loginInfo = params
    loggerserver.info("loadocr...")
    ocrPath = r"./matplotlibes/matp.exe"
    if not os.path.exists(ocrPath):
        loggerserver(f"未在以下路径找到引擎！\n{ocrPath}")
    ocr = OcrAPI(ocrPath)
    print(ocr.getTest())
    loggerserver.info("启动服务。。。")
    webAppServer.run(port=port)


@webAppServer.route('/getWx', methods=['POST'])
def getWx():
    print("开始获取微信")
    pythoncom.CoInitialize()
    wxAuToToolObj = WxAuToTool(1)
    result = "";
    for key, value in wxAuToToolObj.WeChat.my_HWND_dict.items():
        childStr = str(key) +"|" +str(value)
        result=result + ":"+childStr
    print(f"获取微信结果：{result}")
    pythoncom.CoUninitialize()
    print(f"返回微信结果：{result[1:]}")
    return result[1:]

queueOne = Queue()
queueTwo = Queue()
queueOneMsg = Queue()
queueTwoMsg = Queue()
queueOne进度 = Queue()
queueTwo进度 = Queue()
@webAppServer.route('/wxAuToStart', methods=['POST'])
def wxAuToStart():
    requestStr = request.data.decode("utf-8").replace("\\", "/")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            whoStr = getData['whos']
            cheNum = getData['cheNum']
            攻略text = getData['glText']
            攻略imgPath = getData['glPath']
            print(f"攻略text:{攻略text}")
            print(f"攻略imgPath:{攻略imgPath}")
            whos = whoStr.split("|")
            whos = list(filter(None, whos))
            hwndObjInIt(hwnd,whos,cheNum,攻略text,攻略imgPath)
    return ""

@webAppServer.route('/wxSend', methods=['POST'])
def wxSend():
    requestStr = request.data.decode("utf-8").replace("\\", "/")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        wxStr = getData['wxStr']
        if hwnd > 0:
            if "当前合作进度" in wxStr or "当前寒冰进度" in wxStr:
                if hwndObjdickGet(webAppServer.hwndOneObj) == hwnd:
                    loggerserver.info(f"{hwnd}:{wxStr}")
                    try:
                        while not queueOne进度.empty():
                            queueOne进度.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                       print("queueOne进度清空消息")
                    queueOne进度.put(wxStr)
                elif hwndObjdickGet(webAppServer.hwndTwoObj) == hwnd:
                    loggerserver.info(f"{hwnd}:{wxStr}")
                    try:
                        while not queueTwo进度.empty():
                            queueTwo进度.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                        print("queueTwo进度清空消息")
                    queueTwo进度.put(wxStr)
            else:
                if len(webAppServer.hwndOneObj) > 0 and len(wxStr) > 0:
                    if hwndObjdickGet(webAppServer.hwndOneObj) == hwnd:
                        webAppServer.hwndOneObj = {"hwnd": hwnd, 'wxStr': wxStr}
                        loggerserver.info("我是hwndOneObj")
                        queueOne.put(wxStr)
                if len(webAppServer.hwndTwoObj) > 0 and len(wxStr) > 0:
                    if hwndObjdickGet(webAppServer.hwndTwoObj) == hwnd:
                        webAppServer.hwndTwoObj = {"hwnd": hwnd, 'other': wxStr}
                        loggerserver.info("hwndTwoObj")
                        queueTwo.put(wxStr)

            if "退出" in wxStr:
                if hwndObjdickGet(webAppServer.hwndOneObj) == hwnd:
                    loggerserver.info(f"{hwnd}:hwndOneObj退出")
                    webAppServer.hwndOneObj = {}
                    try:
                        while not queueOne.empty():
                            queueOne.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                       print("queueOne清空消息")

                    try:
                        while not queueOne进度.empty():
                            queueOne进度.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                        print("queueOne进度清空消息")

                    queueOne.put(wxStr)
                elif hwndObjdickGet(webAppServer.hwndTwoObj) == hwnd:
                    loggerserver.info(f"{hwnd}:hwndTwoObj退出")
                    webAppServer.hwndTwoObj = {}
                    try:
                        while not queueTwo.empty():
                            queueTwo.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                        print("queueTwo清空消息")

                    try:
                        while not queueTwo进度.empty():
                            queueTwo进度.get_nowait()  # 或者使用 q.get() 如果不想抛出异常
                    except Exception as e:
                        print("queueTwo进度清空消息")
                    queueTwo.put(wxStr)

    return wxStr

@webAppServer.route('/getWxMsg', methods=['POST'])
def getWxMsg():
    requestStr = request.data.decode("utf-8")
    if len(requestStr) > 0:
        getData = json.loads(requestStr)
        hwnd = getData['hwnd']
        if hwnd > 0:
            if hwndObjdickGet(webAppServer.hwndOneObj) == hwnd:
                loggerserver.info(f"{hwnd}:hwndOneObj-GetWxMsg")
                try:
                    wxMsg = queueOneMsg.get(block=False)  # 阻塞直到有元素可用
                    print(f"wxMsg:{wxMsg}")
                    if wxMsg == '退出':
                        print("检测到发出微信车退出指令，现在开始退出。。。")
                        return
                except Exception as e:
                    #print(f"queueObj.get错误:{e}")
                    wxMsg =''
                return wxMsg
            elif hwndObjdickGet(webAppServer.hwndTwoObj) == hwnd:
                loggerserver.info(f"{hwnd}:hwndTwoObj-GetWxMsg")
                try:
                    wxMsg = queueTwoMsg.get(block=False)  # 阻塞直到有元素可用
                    print(f"wxMsg:{wxMsg}")
                    if wxMsg == '退出':
                        print("检测到发出微信车退出指令，现在开始退出。。。")
                        return
                except Exception as e:
                    # print(f"queueObj.get错误:{e}")
                    wxMsg = ''
                return wxMsg
    return ""


webAppServer.hwndOneObj={}
webAppServer.hwndTwoObj={}
def hwndObjInIt(hwnd,whos,cheNum,攻略text,攻略imgPath):
    if len(webAppServer.hwndOneObj) <= 0 and hwndObjdickGet(webAppServer.hwndTwoObj) != hwnd:
        loggerserver.info("hwndOneObj初始化")
        webAppServer.hwndOneObj = {"hwnd": hwnd}
        wxT = threading.Thread(target=wxWorker, args=(whos, hwnd,cheNum,攻略text,攻略imgPath, queueOne,queueOneMsg,queueOne进度))
        wxT.start()
    elif len(webAppServer.hwndTwoObj) <= 0 and hwndObjdickGet(webAppServer.hwndOneObj) != hwnd:
        loggerserver.info("hwndTwoObj初始化")
        webAppServer.hwndTwoObj = {"hwnd": hwnd}
        wxT = threading.Thread(target=wxWorker, args=(whos, hwnd,cheNum,攻略text,攻略imgPath, queueOne,queueTwoMsg,queueTwo进度))
        wxT.start()


def hwndObjdickGet(hwndObjdick):
    for key, value in hwndObjdick.items():
        return value
def wxWorker(whos, hwnd,cheNum,攻略text,攻略imgPath,queue,queueMsg,queue进度):
    pythoncom.CoInitialize()
    wxAuToTool = WxAuToTool(0)
    wxAuToTool.queueObj = queue
    wxAuToTool.queueMsgObj = queueMsg
    wxAuToTool.queue进度 = queue进度
    wxAuToTool.cheNum = cheNum
    wxAuToTool.攻略text = 攻略text
    wxAuToTool.攻略imgPath = 攻略imgPath
    wxAuToTool.wxWinHwndReg(whos,hwnd)
    wxAuToTool.wxAuToStart()
    pythoncom.CoUninitialize()






