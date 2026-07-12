import zipfile
import os
"""
src_path:压缩包所在文件路径
target_path:压缩后文件存放路径
"""
src_path="I:\\zip\\zip.zip"
target_path="I:\\zip"
if os.path.isdir(target_path) == True:
    print("aaaaa")
    z = zipfile.ZipFile(src_path, 'r')
    z.extractall(path=target_path)
    z.close()
