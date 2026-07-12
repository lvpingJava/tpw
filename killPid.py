import os
import time
from stat import S_IWRITE
import psutil

class clear:
    def getPaths(slef,name):
        pathAll=[]
        slef.paths= []
        pids = psutil.process_iter()
        for pid in pids:
            if(pid.name() == name):
                filePath = pid.exe()
                pathAll.append(filePath)
        pathAll = list(dict.fromkeys(pathAll))
        print(pathAll)

        for path in pathAll:
            if path.find("RadiumWMPF") > 0:
                len = path.find("RadiumWMPF")
                newPath = path[0:len + 11]
                slef.paths.append(newPath)
            elif path.find("WmpfRuntime") > 0:
                #len = path.find("WmpfRuntime")
                #newPath = path[0:len + 12]
                #slef.paths.append(newPath)
                pass
            elif path.find("WMPFSDK") > 0:
                len = path.find("WMPFSDK")
                newPath = path[0:len+ 8]
                slef.paths.append(newPath)
        print(slef.paths)
        return slef.paths


    def del_files(self,path):
        try:
            del_list = os.listdir(path)
            for f in del_list:

                file_path = os.path.join(path, f)
                # 不删除当前的py文件
                if os.path.isfile(file_path):
                    print(f"文件路径：{file_path}")
                    # 删除文件
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"没有权限，赋予权限再删除：{e}")
                        os.chmod(file_path, S_IWRITE)
                        os.remove(file_path)
                # 如果是文件夹就递归下去
                elif os.path.isdir(file_path):
                    print(f"文件夹路径：{file_path}")
                    self.del_files(file_path)
        except Exception as e:
            print(f"拒绝访问，没权限：{e}")

    def info(self):
        paths = self.getPaths("WeChatAppEx.exe")
        try:
            os.system('taskkill /f /im %s' % 'AndrowsStore.exe')
        except Exception as e:
            print(f"AndrowsStore结束经常异常：{e}")
        try:
            os.system('taskkill /f /im %s' % 'Androws.exe')
        except Exception as e:
            print(f"Androws.exe结束经常异常：{e}")

        try:
            os.system('taskkill /f /im %s' % 'WeChat.exe')
        except Exception as e:
            print(f"WeChat结束经常异常：{e}")
        try:
            os.system('taskkill /f /im %s' % 'AppMarket.exe')
        except Exception as e:
            print(f"AppMarket结束经常异常：{e}")
        try:
            os.system('taskkill /f /im %s' % 'WeChatAppEx.exe')
        except Exception as e:
            print(f"WeChatAppEx结束经常异常：{e}")

        print("缓存清理中")
        time.sleep(5)

        for path in paths:
            print(f"开始清理：{path}")
            self.del_files(path)

        print("游戏清理已完成")

if __name__ == '__main__':
    cl = clear()
    cl.info()


