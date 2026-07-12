import requests
import subprocess
import os
import keepachangelog
class launch_app():

    def __init__(self) -> None:
        remote_info_url = "http://192.168.3.107/info.json"
        remote_version = self.get_remote_version(remote_info_url)
        local_version = self.get_version()

        ret = self.compared_version(local_version, remote_version)

        if ret == -1:
            update_app = subprocess.Popen("update_app.exe")
            update_app.wait()

        else:
            path = os.path.join(os.getcwd(), 'tof_measurement_tool.dist\\tof_measurement_tool.exe')
            tof_measurement_tool = subprocess.Popen(path)
            tof_measurement_tool.wait()


    def get_version(self):
        changelog = keepachangelog.to_dict(os.path.join(os.getcwd(), 'tof_measurement_tool\\CHANGELOG.md'))
        return list(changelog.keys())[0]


    def get_remote_version(self, url):
        context_res = requests.get(url)
        version = context_res.json()['version']
        return version


    def compared_version(self, ver1, ver2):
        list1 = str(ver1).split(".")
        list2 = str(ver2).split(".")
        # 循环次数为短的列表的len
        for i in range(len(list1)) if len(list1) < len(list2) else range(len(list2)):
            if int(list1[i]) == int(list2[i]):
                pass
            elif int(list1[i]) < int(list2[i]):
                return -1
            else:
                return 1
        # 循环结束，哪个列表长哪个版本号高
        if len(list1) == len(list2):
            return 0
        elif len(list1) < len(list2):
            return -1
        else:
            return 1
