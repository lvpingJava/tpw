import time
from threading import Thread
import multiprocessing
import time

class MyThread(Thread):
    def __init__(self,name):
        Thread.__init__(self) # 初始化线程类
        self.name = name
    def run(self):
        for i in range(1000):
            print("%s"%self.name, i)
            time.sleep(1)



def task():
    while True:
        print("任务执行中")
        time.sleep(0.5)
        t1 = MyThread('线程111')
        t1.start()
        childw()
    print("我结束了啊啊啊啊22222")
def childw():
    while True:
        print("子任务任务执行中")
        t2 = MyThread('进线程22222')
        t2.start()
        time.sleep(0.6)
    print("我结束了啊啊啊啊1")


if __name__ == '__main__':
    sub_task = multiprocessing.Process(target=task)
    # 把子进程设置为守护主进程
    sub_task.daemon = True
    print(f"sub_task:{sub_task}")
    sub_task.start()

    time.sleep(5)
    sub_task.terminate()
    print("结束11111")

    print(f"sub_task:{sub_task}")
    sub_task = multiprocessing.Process(target=task)
    sub_task.daemon = True
    time.sleep(5)
    print("再次启动11111")
    sub_task.start()
    time.sleep(5)
    sub_task.terminate()
    time.sleep(5)
    sub_task = multiprocessing.Process(target=task)
    sub_task.daemon = True
    print("再次启动2222")
    sub_task.start()
    time.sleep(5)
    sub_task.terminate()
    time.sleep(5)
    sub_task = multiprocessing.Process(target=task)
    sub_task.daemon = True
    print("再次启动3333")
    sub_task.start()
    time.sleep(5)
    sub_task.terminate()
    time.sleep(5)
    sub_task = multiprocessing.Process(target=task)
    sub_task.daemon = True
    print("再次启动4444")
    sub_task.start()

