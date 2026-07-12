from wxauto import WeChat
import time
wx = WeChat()
who ='小毛毛鱼'
# 发送消息
wx = WeChat()

# 指定监听目标
listen_list = [
    who
]
for i in listen_list:
    wx.AddListenChat(who=i, savepic=True)  # 添加监听对象并且自动保存新消息图片

chataa = wx.GetListenObj(who)
chataa.SendMsg("当前空车"
               "\n合作9号上车发：合作9号1234"
               "\n寒冰9号上车发：寒冰9号1234"
               "\n攻略查询：发送：攻略查询")
# 持续监听消息，并且收到消息后回复“收到”
wait = 1  # 设置1秒查看一次是否有新消息
i = 0
while True:
    msgs = wx.GetListenMessage()

    for chat in msgs:
        msg = msgs.get(chat)  # 获取消息内容
        if i == 0:
            msg={}
        i = 1
        print(f"msg:{msg}")
        if(msg):
            for sublist in msg:
                for item in sublist:
                    if ("合作9号" in item) or  ("寒冰9号" in item):
                        chat.SendMsg(item+':已上车')
                        i = 0
                        time.sleep(5)
                    if "攻略查询" in item:
                        chat.SendMsg("攻略：上魇、傀、葵、咕咕、冰骑、亡将，其他带几个球，全上升满挂机。有钱帮着换强袭")
                        files = ['I:/wxtup.jpg']
                        chat.SendFiles(files)
                        i = 0
                        time.sleep(5)
                    # 回复收到
        #chat.SendMsg('收到')  # 回复收到
    time.sleep(wait)