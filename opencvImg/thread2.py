import time


def test(a):
    print(a)
    if a > 0:
        a -=1

        test(a)

start_time = time.time()
testss = test(10)
end_time = time.time()
print("FindPicS程序运行时间：%.2f秒" % (end_time - start_time))