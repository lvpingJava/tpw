
import time
from multiprocessing import Process

import DmTool
import fcnS
from pyLog import Log

logger = Log().get_log()

class FightThread(Process):
    def __init__(self, hwnd,battleCard):
        super(FightThread, self).__init__()
        self.hwnd = hwnd
        self.battleCard = battleCard
        self.tag = 0
        self.nowFight = 0
        logger.info("对战初始化线程完成")

    def run(self):
        try:
            logger.info("开始对战")
            res = DmTool.FindStr(self.hwnd, "对战", 808, 533, 989, 600)
            DmTool.leftClick(self.hwnd, res[0], res[1])
            count = 100
            while count > 0 and self.nowFight >= 0:
                res = DmTool.FindStr(self.hwnd, "匹配", 653, 513, 742, 543)
                if len(res) != 0:
                    DmTool.leftClick(self.hwnd, res[0], res[1])
                    count = -1
                count -= 1

            count = 100
            # 当前在战斗中
            self.nowFight = 0
            while count > 0 and self.nowFight >= 0:
                res = DmTool.FindPic(self.hwnd, "刷新标志.tif", 680, 524, 763, 576, 0.8, 1)
                if len(res) != 0:
                    count = -1
                    self.nowFight = 1
                count -= 1
                logger.info("没有进入对战，等待刷新中.....")
                time.sleep(0.5)

            fightOutCount = 0  # 是否已离开对战
            # 对战逻辑处理中
            while self.nowFight > 0 and self.nowFight >= 0:
                # 上卡逻辑处理
                count = 100
                isHave = 0
                while count > 0 and self.nowFight >= 0:
                    resCards = DmTool.FindPicS(self.hwnd, self.battleCard, 392, 512, 646, 614, 0.8)
                    if len(resCards) == 3:
                        count = -1
                    elif len(resCards) > 0:
                        isHave += 1

                    if isHave > 1:
                        count = -1
                    count -= 1
                    time.sleep(0.1)

                if len(resCards) > 0:
                    # 卡牌执行
                    logger.info("上卡执行")
                    fcnS.cardHandler(self.hwnd, resCards,self.op)

                # 判断当前是否在对战中
                res = DmTool.FindPic(self.hwnd, "刷新标志.tif", 680, 524, 763, 576, 0.8, 1)
                if len(res) == 0:
                    while fightOutCount > 10 and self.nowFight >= 0:
                        res = DmTool.FindPic(self.hwnd, "刷新标志.tif", 680, 524, 763, 576, 0.8, 1)
                        if len(res) == 0:
                            fightOutCount += 1
                        else:
                            fightOutCount = 0
                        time.sleep(0.02)
                    if fightOutCount > 10:
                        print("对战结束了")
                        self.nowFight = 0


            print("线程结束了")
        except Exception as e:
            logger.info("发生异常：", str(e))
        finally:
            logger.info('通过异常线程结束')



