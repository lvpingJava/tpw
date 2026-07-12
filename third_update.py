
import requests
from tqdm import tqdm

def downloadFILE(url,name):
    resp = requests.get(url=url,stream=True)
	#stream=True的作用是仅让响应头被下载，连接保持打开状态，
    content_size = int(resp.headers['Content-Length'])/1024		#确定整个安装包的大小
    with open("aaaaa.exe", "wb") as f:
        print(f"安装包整个大小是：{round(content_size/1024, 1)}M，开始下载...")
        for data in tqdm(iterable=resp.iter_content(1024),total=content_size,unit='k',desc=name):
	#调用iter_content，一块一块的遍历要下载的内容，搭配stream=True，此时才开始真正的下载
	#iterable：可迭代的进度条 total：总的迭代次数 desc：进度条的前缀
            f.write(data)
        print(name + "已经下载完毕！")

if __name__ == '__main__':
    url = "https://store4.lanosso.com/1011110020918675bb/2020/04/15/b29a0cd5962a9399beb957085057469e.exe?st=cT9ISj5ruISFfGC7x0zpeA&e=1696996838&b=ArYBtFTfUL1QqgPAUuQOnFWHW_bMDuVHhB3oBaVQrUjU_c&fi=20918675&pid=210-22-95-59&up=2&mp=0&co=0"
    downloadFILE(url,"躺平王辅助")