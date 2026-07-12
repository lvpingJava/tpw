from wxauto import WeChat
import time

wx = WeChat(type=2)


who ='小毛毛鱼'
who2 ='文件传输助手'
who3 ='塔防辅助1群'
who4 ='躺平王辅助2群'
for key, value in wx.my_HWND_dict.items():
    print(key, value)
    # 发送消息
    wx = WeChat(hwnd=value)


# 指定监听目标
listen_list = [
    who,
    who2,
    who3,
    who4
]
def listenInfo(listen_list,type=1):
    if type == 1:
        for whoObj in listen_list:
            wx.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
            time.sleep(0.5)
            wx.SendMsg("当前空车"
                           "\n合作9号上车发：合作9号1234"
                           "\n寒冰9号上车发：寒冰9号1234"
                           "\n攻略查询：发送：攻略查询"
                           "\n进度查询：发送：进度查询",whoObj)
    else:
        for whoObj in listen_list:
            wx.AddListenChat(who=whoObj, savepic=False)  # 添加监听对象并且自动保存新消息图片
            time.sleep(1)



listenInfo(listen_list)
# 持续监听消息，并且收到消息后回复“收到”
wait = 1.5  # 设置1秒查看一次是否有新消息
while True:
    try:
        msgs = wx.GetListenMessage()
        print(f"msgs:{msgs}")
        for chat in msgs:
            print(chat)
            msg = msgs.get(chat)  # 获取消息内容


            if(msg):
                for sublist in msg:
                    mySelf =''
                    for item in sublist:
                        if 'Self' in item:
                            mySelf = 'Self'
                            print("当前Self")
                        elif mySelf == 'Self' and "当前空车" in item:
                            print("当前空车")
                        else:
                            if ("合作9号" in item) or ("寒冰9号" in item):
                                chat.SendMsg(item+':已上车')
                                time.sleep(0.5)
                            elif "攻略查询" in item:
                                chat.SendMsg("攻略：上魇、傀、葵、咕咕、冰骑、亡将，其他带几个球，全上升满挂机。有钱帮着换强袭")
                                files = ['I:/wxtup.jpg']
                                chat.SendFiles(files)
                                time.sleep(0.5)
                            elif "进度查询" in item:
                                chat.SendMsg('当前进度为：101关')
                                time.sleep(0.5)
                            # 回复收到

    except Exception as e:
        print(f"微信聊天对象不存在，或关闭：异常信息:{e}")
        listenInfo(listen_list,0)
    time.sleep(wait)