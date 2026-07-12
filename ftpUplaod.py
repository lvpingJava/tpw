import os
from ftplib import FTP
# 连接ftp服务器
from tqdm import tqdm


def ftpConnect(ftpserver, port, usrname, password):
    ftp = FTP()
    try:
        ftp.connect(ftpserver, port)
        ftp.login(usrname, password)
    except:
        raise IOError('\n FTP connection failed, please check the code!')
    else:
        print(ftp.getwelcome())  # 打印登陆成功后的欢迎信息
        print('\n+------- ftp connection successful!!! --------+')
        return ftp


# 下载单个文件
def ftpDownloadFile(ftp, ftpfile, filename):
    with open(filename, 'wb') as fd:
        total = ftp.size(filename)
        print(f"躺平王辅助更新包大小是：{round(total/1024/1024, 1)}M，开始下载...")
        with tqdm(total=total) as pbar:
            def callback_(data):
                l = len(data)
                pbar.update(l)
                fd.write(data)

            ftp.retrbinary('RETR {}'.format(filename), callback_)
    return True



# 下载整个目录下的文件
def ftpDownload(ftp, ftpaths, localpath):
    try:
        if not os.path.exists(localpath):
            os.makedirs(localpath)
        paths = ["tpw6.1","tpw6.1.1"]
        for ftppath in paths:
            ftp.cwd(ftppath)
            for file in ftp.nlst():
                if "." != file and ".." != file:
                    ftpDownloadFile(ftp, file, file)
            ftp.cwd('..')
    except Exception as e:
        pass
    finally:
        ftp.quit()
        return True


# 退出ftp连接
def ftpDisConnect(ftp):
    ftp.quit()


# 程序入口
if __name__ == '__main__':
    # 输入参数
    ftpserver = '47.101.48.90'
    port = 21
    usrname = 'lp_lp'
    pwd = 'TCwZbxS4k36jBCpm'
    ftpath = "/"
    localpath = 'I:/data/'

    ftp = ftpConnect(ftpserver, 21, usrname, pwd)
    flag = ftpDownload(ftp, ftpath, localpath)

