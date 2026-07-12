import os
import shutil

import numpy as np

path = os.path.dirname(os.path.realpath(__file__))
fileName = path + "\手牌"
if os.path.isdir(fileName) == False:
    print("配置文件夹不存在")
else:
    isBool = 1
    #path = "C:\\test_game\\版本号.txt"
    #f = open(path, encoding="utf-8")
    #if f.read(10) == self.ver:
     #   isBool = 0
    #f.close()
    listdirs = os.listdir(fileName)
    for file in listdirs:
        print(f"aaaa:{file}")
        src_path = fileName+"\\"+file
        dst_path = path + "\\快速手牌\\"+file
        listdirs = os.listdir(dst_path)
        for file in listdirs:

            dst_pathTem = src_path + "\\"+file
            if os.path.exists(dst_pathTem):
                print(f"文件存在:{dst_pathTem}")
                pass
            else:
                shutil.copy(dst_path+"\\"+file,src_path)
                print(file)



'''path ="C:\\aaaa\\a.txt"
path1 ="C:\\aaaa\\b.txt"
# 该文件存放内容如下：
# Study python I can learn a lot
# Study python I can programming
# Study python I can be happier
strDatas = []
with open(path,'r',encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())
        strDatas.append(line.strip())

print(strDatas)
np.savetxt(path1, strDatas, delimiter=',', fmt='%s')'''


'''data = np.loadtxt(path, delimiter=",", dtype=str,encoding="utf-8")
print(data, data.dtype)
data = data.astype('<U50')
np.savetxt(path1, data, delimiter=',', fmt='%s')'''


'''path ="C:\\aaaa\\版本号.txt"
f = open(path, encoding="utf-8")
if f.read(10) == "5.8.7.5":
    print("aaaaaa")
f.close()


path ="C:\\aaaa"
f = open(path+"\\a.txt", "w")
f.write("aaaa1")
f = open(path+"\\b.txt", "w")
f.write("aaaa2")
f = open(path+"\\c.txt", "w")
f.write("aaaa3")
f.close()'''