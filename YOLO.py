import requests

class YoloOBJ:
    def __init__(self, obj_id=0, x=0, y=0, w=0, h=0, prob=0, name=''):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.prob = prob
        self.name = name

class Yolo:
    def __split_my_yolo(self, ret, confience):
        yolo_obj_list = list()
        m_num = 0
        m_list = ret.text.split("|")
        for i in m_list:
            list2 = i.split(",")
            if len(list2) >= 7:
                temp_arr = YoloOBJ()
                temp_arr.obj_id = list2[0]
                temp_arr.x = list2[1]
                temp_arr.y = list2[2]
                temp_arr.w = list2[3]
                temp_arr.h = list2[4]
                temp_arr.prob = list2[5]
                temp_arr.name = list2[6]
                if float(temp_arr.prob)>= confience:
                    yolo_obj_list.append(temp_arr)
                    m_num = m_num + 1
        return yolo_obj_list, m_num

    def post_hwnd(self, hwnd, confience=0.2, post_url='http://10.50.8.250:7700/hwnd'):
        # 仅本机可用
        # 将本机的目标窗口句柄通过POST发送给检测器，检测器自动对该窗口进行截图然后识别，返回结果
        # 本机请求地址为127.0.0.1
        # 注意IP地址和端口号正确填写
        # 链接开头为http，不是https
        m_hwnd = str(hwnd)  # 填目标窗口句柄则识别该窗口返回结果
        ret = requests.post(post_url, data=m_hwnd)
        ret_list, obj_num = self.__split_my_yolo(ret, confience)
        return ret_list, obj_num, ret.text

    def post_file(self, pic_file, confience=0.2, post_url='http://127.0.0.1:7700/file'):
        # 仅本机可用
        # 将本机图片路径通过POST发送给检测器，检测器读入图片然后识别，返回结果
        # 本机请求地址为127.0.0.1
        # 注意IP地址和端口号正确填写
        # 链接开头为http，不是https
        m_file = pic_file.encode('utf-8')
        ret = requests.post(post_url, data=m_file)
        ret_list, obj_num = self.__split_my_yolo(ret, confience)
        return ret_list, obj_num, ret.text

    def post_pic(self, pic_bytes, confience=0.9, post_url='http://10.50.8.250:7700/pic'):
        # 可跨电脑使用
        # 将图片bytes通过POST发送给检测器，检测器自动对该窗口进行截图然后识别，返回结果
        # 本机请求地址为127.0.0.1；如果为局域网则查看启动检测器那台电脑的局域网IP即可，一般为192.168.x.x；若为公网需要有公网且对应的端口已开放（注意80、443端口没备案或家宽一般被禁用用不了的）
        # 注意IP地址和端口号正确填写
        # 链接开头为http，不是https
        ret = requests.post(post_url, data=pic_bytes)
        ret_list, obj_num = self.__split_my_yolo(ret, confience)
        return ret_list, obj_num, ret.text

    def post_base64(self, pic_base64, confience=0.2, post_url='http://127.0.0.1:7700/base64'):
        # 可跨电脑使用
        # 将图片转为base64字符串通过POST发送给检测器，检测器读入图片然后识别，返回结果
        # 本机请求地址为127.0.0.1；如果为局域网则查看启动检测器那台电脑的局域网IP即可，一般为192.168.x.x；若为公网需要有公网且对应的端口已开放（注意80、443端口没备案或家宽一般被禁用用不了的）
        # 注意IP地址和端口号正确填写
        # 链接开头为http，不是https
        ret = requests.post(post_url, data=pic_base64)
        ret_list, obj_num = self.__split_my_yolo(ret, confience)
        return ret_list, obj_num, ret.text