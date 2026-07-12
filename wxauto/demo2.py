from wxauto import WeChat
import time

def wxInfo(who:str):
    wx = WeChat()
    #who ='小毛毛鱼'
    who2 =who
    #发送消息
    wx = WeChat()

    # 指定监听目标
    listen_list = [
        who
    ]

    for whoObj in listen_list:
        wx.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
        #chat = wx.GetListenObj(whoObj)
        time.sleep(0.5)
        wx.SendMsg("当前空车"
                       "\n合作9号上车发：合作9号1234"
                       "\n寒冰9号上车发：寒冰9号1234"
                       "\n攻略查询：发送：攻略查询"
                       "\n进度查询：发送：进度查询",whoObj)
    # 持续监听消息，并且收到消息后回复“收到”
    wait = 2  # 设置1秒查看一次是否有新消息
    state = 0
    while True:
        msgs = wx.GetListenMessage()
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
                        # if item == 'Self' and state == 1:
                        #     state = 0
                        #     break
                        if ("合作9号" in item) or ("寒冰9号" in item):
                            chat.SendMsg(item+':已上车')
                            state = 0
                            time.sleep(1)
                        elif "攻略查询" in item:
                            chat.SendMsg("攻略：上魇、傀、葵、咕咕、冰骑、亡将，其他带几个球，全上升满挂机。有钱帮着换强袭")
                            files = ['I:/wxtup.jpg']
                            chat.SendFiles(files)
                            state = 0
                            time.sleep(1)
                        elif "进度查询" in item:
                            chat.SendMsg('当前进度为：101关')
                            state = 0
                            time.sleep(1)
                        # 回复收到
        time.sleep(wait)