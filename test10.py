import json

import requests
import base64



if __name__ == '__main__':

    cookie = "token=code_space;"
    header = {
        "cookie": cookie,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    }
    # 发送字典
    post_dict = {'key1': 'value1', 'key2': 'value2'}
    # 发送元组
    post_tuple = (('key1', 'value1'), ('key1', 'value2'))
    # 发送json
    post_json = json.dumps({'some': 'data'})
    r1 = requests.post("http://127.0.0.1:5000/findPic", data=post_dict, headers=header, cookie=cookie)
    r2 = requests.post("http://127.0.0.1:5000/findPic", data=post_tuple, headers=header, cookie=cookie)
    r3 = requests.post("http://127.0.0.1:5000/findPic", data=post_json, headers=header, cookie=cookie)
    print("r1返回的内容为-->" + r1.text)
    print("r2返回的内容为-->" + r2.text)
    print("r3返回的内容为-->" + r3.text)

