from time import sleep
from requests import get
from zipfile import ZipFile, BadZipFile
from os import path,remove,system
from tqdm import tqdm

class tpw_update:

    def chek(self):
        # tpwVer 版本对比
        # Download_addres = 'http://47.101.48.90:8888/down/xFr6oM2JVYYo'
        # 把下载地址发送给requests模块
        # f = get(Download_addres)
        # 下载文件
        remoteContent = "111"
        print("版本更新信息如下：")
        print(remoteContent)
        # f.close()

        lines = remoteContent.split("\r")
        if len(lines) > 0:
            first_line = lines[0]
            #打开文件
            localFile = open('./models/tpwVer.txt', 'r',encoding='ISO8859-1')
            # 读取文件内容
            localContent = localFile.read()
            # 关闭文件
            localFile.close()
            locacver =""
            locallines = localContent.split("\n")
            if len(locallines) > 0:
                localfirst_line = locallines[0]
                locacver = localfirst_line
            if locacver.strip()== first_line.strip():
                print("版本匹配")
            else:
                # 更新文件内容
                content = localContent.replace(localContent, first_line)
                # 打开文件
                file = open('./models/tpwVer.txt', 'w')
                # 写入更新后的内容
                file.write(content)
                # 关闭文件
                file.close()

    def down(slef):
          ''''#下载地址Dan0ZgRqY0rC

          #把下载地址发送给requests模块
          f=get(Download_addres)
          #下载文件
          with open("update.zip","wb") as code:
               code.write(f.content)'''
          Download_addres = 'http://47.101.48.90:8888/down/AaDbjDNqeIuC'
          resp = get(url=Download_addres, stream=True)
          # stream=True的作用是仅让响应头被下载，连接保持打开状态，
          content_size = int(resp.headers['Content-Length']) / 1024  # 确定整个安装包的大小
          with open("update.zip", "wb") as f:
              print(f"躺平王辅助更新包大小是：{round(content_size / 1024, 1)}M，开始下载...")
              for data in tqdm(iterable=resp.iter_content(1024), total=content_size, unit='k', desc="躺平王辅助下载中..."):
                  # 调用iter_content，一块一块的遍历要下载的内容，搭配stream=True，此时才开始真正的下载
                  # iterable：可迭代的进度条 total：总的迭代次数 desc：进度条的前缀
                  f.write(data)
              print("躺平王辅助已下载完毕！")
              sleep(1)
    def work(self):
          src_path = "update.zip"
          target_path = "./"
          if path.isdir(target_path) == True:
               print("开始解压")
               # z = ZipFile(src_path, 'r')
               # z.extractall(path=target_path)
               # z.close()
               try:
                   with ZipFile(src_path, 'r') as zip_ref:
                       zip_ref.extractall(target_path)
                   print(f"ZIP 文件已成功解压到 {target_path}")
               except PermissionError as e:
                   print(f"权限错误：{e}")
                   print(f"请确保你有权限读取 {src_path} 和写入 {target_path}")
               except BadZipFile:
                   print(f"ZIP 文件已损坏或不是有效的 ZIP 文件。")
               except Exception as e:
                   print(f"在解压过程中发生了一个未知错误：{e}")
          remove("update.zip")
          print("软件更新中已完成100%。。。")
if __name__ == '__main__':
    tp = tpw_update()
    print("软件更新中，请稍等，请不要退出,更新完成后会自动退出的。。。")
    try:
        system('taskkill /f /im %s' % '躺平王客户端.exe')
    except Exception as e:
        pass


    for i in range(6):
        print(f"软件更新中已完成{i+1}0%。。。")
        sleep(1)

    try:
        system('taskkill /f /im %s' % '躺平王服务端.exe')
    except Exception as e:
        pass

    try:
        system('taskkill /f /im %s' % 'Runner.exe')
    except Exception as e:
        pass

    tp.down()
    print("软件更新中已完成70%。。。")
    tp.work()
    sleep(1)
    tp.chek()
    print("软件更新中已完成。。。")
    sleep(3)