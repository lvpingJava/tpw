import time
from RkSDK import RkSDK
from RkSDK import Rk初始化软件入参类
from RkSDK import Rk通讯加密方式枚举类
from RkSDK import Rk结果心跳失败类
from PyQt5.QtWidgets import (
    QMessageBox
)
global rksdk
selfObj=None
loginState = 0
rksdk = RkSDK()
rk初始化软件入参 = Rk初始化软件入参类()
def 接收心跳失败的函数(rk结果心跳失败: Rk结果心跳失败类):
    print("错误编码：" + str(rk结果心跳失败.错误编码))
    print("错误消息：" + rk结果心跳失败.错误消息)


    '''time.sleep(1)
    rk结果账号单码详情 = rksdk.账号详情函数()
    if rk结果账号单码详情.错误编码 == 0:
        print("账号详情获取成功，账号到期时间：" + rk结果账号单码详情.到期时间 + "  账号剩余点数：" + str(
            rk结果账号单码详情.剩余点数) + " 备注：" + rk结果账号单码详情.备注)
    else:
        print("单码详情获取失败：" + rk结果账号单码详情.错误消息)'''
    selfObj.webServerStopAll(rk结果心跳失败.错误消息)

    #rksdk.关闭当前软件()

def 单码操作示例(val:str):
    result = -1
    rk初始化软件入参.平台用户编码 = "84bba67300c43639"
    rk初始化软件入参.软件编码 = "337dd7f2cc737070"
    rk初始化软件入参.通讯加密方式 = Rk通讯加密方式枚举类.DES加密
    rk初始化软件入参.加密Key = "aa081177"
    rk初始化软件入参.签名盐 = "d7d24868"
    rk初始化软件入参.软件版本号 = "v1.0"
    rk初始化软件入参.心跳失败的回调函数 = 接收心跳失败的函数
    rk结果初始化软件 = rksdk.初始化软件函数(rk初始化软件入参)
    result = rk结果初始化软件.错误编码
    if result == 0:
        time.sleep(1)
        rk结果单码登录 = rksdk.单码登录函数(val)
        result = rk结果单码登录.错误编码
        if result == 0:
            # 登录成功后，在此写你自己的业务逻辑代码
            loginState = 1
            global notice
            global version
            notice = rk结果初始化软件.软件信息.软件公告
            version = rk结果初始化软件.软件信息.软件名称
            print("单码登录成功，账号到期时间：" + rk结果单码登录.到期时间 + "  账号剩余点数：" + str(
                rk结果单码登录.剩余点数) + " 备注：" + rk结果单码登录.备注 + " 角色名称：" + rk结果单码登录.角色名称)
        else:
            print("单码登录失败，错误编码：" + str(rk结果单码登录.错误编码) + " 错误消息：" + rk结果单码登录.错误消息)
            result = rk结果单码登录.错误消息

    else:
        print("\n软件初始化失败，错误编码：" + str(rk结果初始化软件.错误编码) + "  错误消息：" + rk结果初始化软件.错误消息)

    return result
def register(val:str):
    return 单码操作示例(val)
def isLogin():
    rk结果单码详情 = rksdk.单码详情函数()
    if rk结果单码详情.错误编码 == 0:
        print("单码详情获取成功，单码到期时间：" + rk结果单码详情.到期时间 + "  单码剩余点数：" + str(
            rk结果单码详情.剩余点数) + " 备注：" + rk结果单码详情.备注)
        return rk结果单码详情.到期时间 + "," + version
    else:
        print("单码详情获取失败：" + rk结果单码详情.错误消息)
        return ""

def getRegisterInfo():
    my_array = []
    my_array.append(version)
    my_array.append(notice)
    return my_array

def 退出登录():
    print("退出登录")
    return rksdk.退出登录函数()



if __name__ == '__main__':
    单码操作示例("7d4f3b11fb1e8994")