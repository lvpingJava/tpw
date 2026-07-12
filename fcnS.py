import time

import DmTool
from log import Log


class FcnS:
    def __init__(self):
        print("FcnS-init")

logger = Log().get_log()

#点击英雄处理
def cardHandler(hwnd,resCards,op):
    for i in resCards:
        card = list(resCards[i].keys())[0]
        cardInfo =resCards[i].get(card)
        DmTool.leftClick(hwnd, cardInfo[0], cardInfo[1])
        isBool = 0
        isBool1 = 0
        count = 10
        while count > 0:
            #res = DmTool.FindPic(self.hwnd, "绿色星星.tif", 9,188,182,477, 0.8, 1)
            res = DmTool.FindPic(hwnd, card, 392,512,646,614, 0.8, 0)
            if len(res) == 0 and isBool1 > 0:
                count = -1
                isBool = 1
            elif len(res) == 0:
                isBool1 += 1
            count -= 1
            time.sleep(0.05)

    if isBool == 1:
        #刷新
        res = DmTool.FindStr(hwnd,"刷新",696,561,757,593)
        if len(res) > 0:
            intX = 0
            intY = 0
            res = op.FindColor(0, 0, 2000, 2000, "", 1.0, 0, intX, intY)
            if res == 0:
                logger.info("有金币了，可以刷新了")
            else:
                logger.warn("金币不够，等待中")


            DmTool.leftClick(hwnd, 722, 576)

    else:
        #扩建
        res = DmTool.FindStr(hwnd, "扩建", 295,570,348,594)
        if len(res) > 0:
            DmTool.leftClick(hwnd, 314, 575)

def FindStrByZuoBiao(hwnd,strs,x: int, y: int, x1: int, y1: int):
    res = DmTool.FindStr(hwnd, strs,  x, y, x1, y1)
    if len(res) > 0:
        return res[0],res[1]
    else:
        return 0

def FindPicZuoBiao(hwnd:int,card,x: int, y: int, x1: int, y1: int,matching:float):
    res = DmTool.FindPic(hwnd, card, x, y, x1, y1,matching)
    if len(res) > 1:
        res = res.split(",")
        return int(res[0]), int(res[1])
    else:
        return 0


