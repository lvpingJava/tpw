# pip install -r requirements.txt
from YOLO import Yolo
import time

if __name__ == '__main__':
    yolo = Yolo()

    while True:
        t1 = time.time()
        ret_list, obj_num, ret = yolo.post_hwnd(hwnd=665906) # 替换为自己电脑上的目标窗口句柄
        t2 = time.time()

        jg = ''
        for i in ret_list:
            jg += 'id:' + i.obj_id + '   x:' + i.x + '   y:' + i.y + '   w:' + i.w + '   h:' + i.h + '   prob:' + i.prob + '   name:' + i.name + '\r\n'
        print('【耗时' + str(int((t2-t1)*1000)) + "ms，共" + str(obj_num) + '个目标】\r\n' + '[返回总文本]' + ret + '\r\n' + jg + '\r\n')