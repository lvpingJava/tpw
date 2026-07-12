from wxauto import WeChat
import time
class WxAuToTool:
    # 初始化方法（构造方法），当创建类的实例时会自动调用
    def __init__(self):
        self.WeChat = WeChat(type=2)
        # 实例方法

    def listenInfo(self,type=1):
        if type == 1:
            for whoObj in self.listen_list:
                self.WeChat.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
                time.sleep(0.5)
                self.WeChat.SendMsg("当前空车"
                               "\n合作9号上车发：合作9号1234"
                               "\n寒冰9号上车发：寒冰9号1234"
                               "\n攻略查询：发送：攻略查询"
                               "\n进度查询：发送：进度查询",whoObj)
        else:
            for whoObj in self.listen_list:
                self.WeChat.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
                print("重启加载窗口")
                time.sleep(0.5)

    def wxWinHwndReg(self,whos):
        self.listen_list = whos
        for key, value in self.WeChat.my_HWND_dict.items():
            print(key, value)
            self.WeChat = WeChat(hwnd=value)

        self.listenInfo(1)

    def wxAuToStart(self):
        wait = 1.5  # 设置1秒查看一次是否有新消息
        state = 0
        while True:
            try:
                msgs = self.WeChat.GetListenMessage()
                print(f"msgs:{msgs}")
                for chat in msgs:
                    print(chat)
                    msg = msgs.get(chat)  # 获取消息内容
                    if state == 0:
                        msg={}
                    state = 1

                    if(msg):
                        for sublist in msg:
                            for item in sublist:
                                # if item == 'Self':
                                #     break
                                if "退出" in item:
                                    print("退出")
                                    return
                                if ("合作9号" in item) or ("寒冰9号" in item):
                                    chat.SendMsg(item+':已上车')
                                    state = 0
                                    time.sleep(0.5)
                                elif "攻略查询" in item:
                                    chat.SendMsg("攻略：上魇、傀、葵、咕咕、冰骑、亡将，其他带几个球，全上升满挂机。有钱帮着换强袭")
                                    files = ['I:/wxtup.jpg']
                                    chat.SendFiles(files)
                                    state = 0
                                    time.sleep(0.5)
                                elif "进度查询" in item:
                                    chat.SendMsg('当前进度为：101关')
                                    state = 0
                                    time.sleep(0.5)
                                # 回复收到

            except Exception as e:
                print(f"微信聊天对象不存在，或关闭：异常信息:{e}")
                self.listenInfo(0)
            time.sleep(wait)


# wxAuToObj =  WxAuToTool()
# wobj = [
#     '小毛毛鱼',
#     '文件传输助手'
# ]
# wxAuToObj.wxWinHwndReg(wobj)
# wxAuToObj.wxAuToStart()
# print("结束了")
# wxAuToObj = None