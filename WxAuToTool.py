from wxauto import WeChat
import time
from datetime import datetime,timedelta
import re
class WxAuToTool:
    # 初始化方法（构造方法），当创建类的实例时会自动调用
    def __init__(self,tag=1):

        if tag == 1:
            print("获取微信")
            self.WeChat = WeChat(type=0)
        else:
            self.queueObj = None
            self.queueMsgObj = None
            self.queue进度 = None
            self.loading = 0
            self.cheNum = 0
            self.攻略text = ''
            self.攻略imgPath = ''
        # 实例方法

    def oneChadMsg(self,whoObj,text):
        chat = self.WeChat.GetListenObj(whoObj)
        chat.SendMsg(text)
    def listenInfo(self,type=1,text=''):
        if type == 1:
            for whoObj in self.listen_list:
                #self.WeChat.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
                time.sleep(0.1)
                self.WeChat.SendMsg(text,whoObj)
        else:
            for whoObj in self.listen_list:
                self.WeChat.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
                print("重启加载窗口")
                time.sleep(0.5)

    def wxWinHwndReg(self,whos,hwnd):
        self.listen_list = whos
        #for key, value in self.WeChat.my_HWND_dict.items():
            #print(key, value)
        self.WeChat = WeChat(hwnd=hwnd)
        self.listenInfo(0)

    def wxAuToStart(self):
        print("wxAuToStart....")
        self.count = 0
        self.进度 = ''
        while True:
            try:

                try:
                    进度查询Str = self.queue进度.get(block=False)
                    print(f"进度查询Str:{进度查询Str}")
                    if '进度' in 进度查询Str:
                        self.进度 = 进度查询Str
                except Exception as e:
                    # print(f"queueObj.get错误:{e}")
                    wxStr = ""

                try:
                    wxStr = self.queueObj.get(block=False)  # 阻塞直到有元素可用
                    print(f"queueWxStr:{wxStr}")
                    if wxStr == '退出':
                        self.loading == 0
                        print("检测到发出微信车退出指令，现在开始退出。。。")
                        try:
                            while not self.queueObj.empty():
                                self.queueObj.get_nowait()  
                        except Exception as e:
                            print("self.queueObj清空消息")

                        try:
                            while not self.queue进度.empty():
                                self.queue进度.get_nowait()  
                        except Exception as e:
                            print("self.queue进度清空消息")
                        return
                    if '进入' in wxStr:
                        print("正在进入房间")
                        self.count = 20
                        if '寒冰' in wxStr:
                            self.count = 30
                        self.loading = 1
                        print(f"count:{ self.count}")
                        #self.listenInfo(type=1,text=wxStr)
                        self.chat.SendMsg(wxStr)

                        try:
                            while not self.queueObj.empty():
                                self.queueObj.get_nowait()  
                        except Exception as e:
                            print("self.queueObj清空消息")

                        try:
                            while not self.queue进度.empty():
                                self.queue进度.get_nowait()  
                        except Exception as e:
                            print("self.queue进度清空消息")

                        continue
                    elif '结束' in wxStr:
                        self.loading = 0
                        #self.listenInfo(type=1,text=wxStr)
                        self.进度=''
                        self.chat.SendMsg(wxStr)
                        try:
                            while not self.queue进度.empty():
                                self.queue进度.get_nowait()  
                        except Exception as e:
                            print("self.queue进度清空消息")

                        continue
                    elif '当前空车' in wxStr:
                        self.loading = 0
                        text = wxStr.split(".:.")
                        self.listenInfo(type=1, text=text[0] + "\n" + text[1]+ "\n攻略查询：发送：攻略查询" + "\n进度查询：发送：进度查询")
                        #self.chat.SendMsg(text[0] + "\n" + text[1])
                        continue
                    elif '.png' in wxStr:
                        files = [wxStr]
                        chat.SendFiles(files)
                        continue
                except Exception as e:
                    # print(f"queueObj.get错误:{e}")
                    wxStr = ""
                print(f"count-start:{self.count}")
                if self.count > 0:
                    self.count = self.count - 1
                    time.sleep(1)
                    print("正在进入房间中，睡眠1秒")
                    continue

                print(f"count-end:{self.count}")
                msgs = self.WeChat.GetListenMessage()
                print(f"msgs:{msgs}")
                for chat in msgs:
                    msg = msgs.get(chat)  # 获取消息内容
                    if(msg):
                        for sublist in msg:
                            mySelf = ''
                            for item in sublist:
                                if 'Self' in item:
                                    mySelf = 'Self'
                                    print("当前Self")
                                elif item == 'Time':
                                    if date比较(str(sublist)) == 0:
                                        print("时间不满足，跳槽循环")
                                        raise Exception
                                elif mySelf == 'Self' and "当前空车" in item:
                                    print("当前空车")
                                else:
                                    cheInfo = str(self.cheNum) + "号房间"
                                    if cheInfo in item and self.loading == 0:
                                        getNums = getNumbers(item)
                                        if getNums > 0:
                                            self.queueMsgObj.put(str(getNums))
                                            self.chat = chat
                                            self.loading == 1
                                    elif "攻略查询" in item:
                                        if self.攻略text:
                                            chat.SendMsg(self.攻略text)
                                        if self.攻略imgPath:
                                            files = [self.攻略imgPath]
                                            chat.SendFiles(files)
                                        if len(self.攻略text) <= 0 and len(self.攻略imgPath) <= 0:
                                            chat.SendMsg("暂无攻略，发车人二货没写")
                                    elif "进度查询" == item.strip():
                                        if len(self.进度) > 0:
                                            chat.SendMsg(self.进度)
                                        else:
                                            chat.SendMsg("当前空车")

            except Exception as e:
                print(f"微信聊天对象不存在，或关闭：异常信息:{e}")
                self.listenInfo(0)
            time.sleep(1.5)

def getNumbers(s):
    try:
        numbers = re.findall(r'\d+', s)  # \d+ 匹配一个或多个数字
        numbers = [int(num) for num in numbers][1]
        if numbers > 999:
            return numbers
        else:
            return 0
    except Exception as e:
        return 0

def date比较(date_str):
    try:
        # 给定的日期时间字符串
        if len(date_str) > 12:
            # 将字符串转换为datetime对象
            date_format = "%Y年%m月%d日 %H:%M"
            date_obj = datetime.strptime(date_str, date_format)
        else:
            match = re.search(r'\d+:\d+', date_str)
            if match:
                number_part = match.group()
                current_time = datetime.now()
                # 将当前时间转换成指定格式
                formatted_time = current_time.strftime("%Y年%m月%d日")
                date_str = formatted_time + " " + number_part
                date_format = "%Y年%m月%d日 %H:%M"
                date_obj = datetime.strptime(date_str, date_format)

        # 获取当前时间
        current_time = datetime.now()
        current_time = current_time - timedelta(minutes=5)
        # 比较两个日期时间
        if date_obj < current_time:
            return 0
        elif date_obj >= current_time:
            return 1
        else:
            return 1
    except Exception as e:
        print("时间比较错误")
    return 1
