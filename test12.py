from matplotlib.path import Path

def 卡牌位置判断(zbs):
    x1 = 392
    y1 = 510
    w1 = 81
    h1 = 104
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p1 = Path([(x1, h1 + y1), (x1, y1), (x1 + w1, y1), (x1 + w1, y1 + h1)])

    w2 = 79
    h2 = 103
    x2 = 479
    y2 = 511
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p2 = Path([(x2, h2 + y2), (x2, y2), (x2 + w2, y2), (x2 + w2, y2 + h2)])

    w3 = 81
    h3 = 100
    x3 = 565
    y3 = 512
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p3 = Path([(x3, h3 + y3), (x3, y3), (x3 + w3, y3), (x3 + w3, y3 + h3)])


    i1 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        # print(f"{x},{y}")
        a = p1.contains_point((x, y))
        if a:
            i1 += 1
        if i1 > 8:
            print("zb1满足要求")
            break


    i2 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        # print(f"{x},{y}")
        a = p2.contains_point((x, y))
        if a:
            i2 += 1
        if i2 > 8:
            print("zb2满足要求")
            break


    i3 = 0
    for data in zbs:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        # print(f"{x},{y}")
        a = p3.contains_point((x, y))
        if a:
            i3 += 1
        if i3 > 8:
            print("zb3满足要求")
            break
if __name__=="__main__":
    x1 = 392
    y1 = 510
    w1 = 81
    h1 = 104
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p1 = Path([(x1, h1+y1), (x1, y1), (x1+w1, y1), (x1+w1, y1+h1)])


    w2 = 79
    h2 = 103
    x2 = 479
    y2 = 511
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p2 = Path([(x2, h2+y2), (x2, y2), (x2+w2, y2), (x2+w2, y2+h2)])


    w3 = 81
    h3 = 100
    x3 = 565
    y3 = 512
    # 左下角的点   # 左上角的点  # 右上角的点  # 右下角的点
    # 构造一个矩形多边形进行测试
    p3 = Path([(x3, h3+y3), (x3, y3), (x3+w3, y3), (x3+w3, y3+h3)])

    #第一张图
    zb1=['438:544', '428:544', '429:581', '432:544', '434:592', '436:562', '437:584', '438:544', '440:581', '439:560', '439:560', '441:565', '444:551', '450:577']
    i1 = 0
    for data in zb1:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        #print(f"{x},{y}")
        a = p1.contains_point((x, y))
        if a:
            i1 += 1
        if i1 > 8:
            print("zb1满足要求")
            break

    #第二张图
    zb2=['502:546', '506:539', '507:566', '507:558', '508:534', '509:552', '514:543', '514:551', '514:551', '519:549', '519:561', '519:561', '522:544', '523:548', '527:573', '527:543', '530:556', '531:545', '532:529', '533:575', '533:575', '533:549', '533:559', '534:571', '537:529', '538:555', '542:544']
    i2 = 0
    for data in zb2:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        #print(f"{x},{y}")
        a = p2.contains_point((x, y))
        if a:
            i2 += 1
        if i2 > 8:
            print("zb2满足要求")
            break

    # 第三张图
    zb3=['588:548', '597:557', '605:566', '606:572', '608:561', '613:578', '614:549', '614:582', '616:566', '616:566', '620:536', '621:563']
    i3 = 0
    for data in zb3:
        rut = data.split(":")
        x = int(rut[0])
        y = int(rut[1])
        #print(f"{x},{y}")
        a = p3.contains_point((x, y))
        if a:
            i3 += 1
        if i3 > 8:
            print("zb3满足要求")
            break







