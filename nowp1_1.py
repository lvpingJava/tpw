import os
import requests
import hashlib
import zipfile
import shutil
'''try:
    from update_app.update_app_ui import Ui_Dialog
except ImportError :
    from update_app_ui import Ui_Dialog
    from PyQt6.QtCore import pyqtSignal,QThread,Qt
    from PyQt6.QtWidgets import QDialog
    from datetime import datetime
    import time
    import subprocessclass down_file_thread(QThread):
    update_speed_sig = pyqtSignal(str)
    update_percent_sig = pyqtSignal(int)


def __init__(self, parent=None):
    super().__init__(parent)
    self.temp = 0
    self.temp_size = 0


def run(self):
    start_time = time.time()
    with open(self.path, 'wb') as file:
        for chunk in self.context_res.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                self.temp_size += len(chunk)
                percent = (self.temp_size / self.context_length) * 100
                if int(percent) == 100:
                    self.update_speed_sig.emit('0 MB/s')
                    self.update_percent_sig.emit(int(percent))
                else:
                    self.update_percent_sig.emit(int(percent))
                if time.time() - start_time > 2:
                    speed = self.formatFloat((self.temp_size - self.temp) / 1024 / 1024 / 2)
                    self.temp = self.temp_size
                    start_time = time.time()
                    self.update_speed_sig.emit(str(speed) + 'MB/s')
            file.flush()
        file.close()


def formatFloat(self, num):
    return '{:.2f}'.format(num)


class show_log_thread(QThread):
    update_log_sig = pyqtSignal(str)
    def init(self,parent=None):
    super().init(parent)

    def run(self):
        for log in self.update_log:
            self.update_log_sig.emit(log)

class update_app(QDialog):
     def init(self):
         super(update_app, self).init()
         self.ui = Ui_Dialog()
         self.ui.setupUi(self)
         #ui设置
         self.ui.speed_label.setText(“0 MB/s”)
         self.ui.plainTextEdit_change_log.setFocusPolicy(Qt.FocusPolicy.NoFocus)
         #本地版本
         # self.local_version = version
         #zip 和json信息链接
         remote_shafile_url = “http://192.168.3.107/info.json”
         remote_logfile_url = “http://192.168.3.107/index.html”
         #下载下来的zip 文件sha
         self.file_sha = ‘’
         #下载的文件路径log
         self.file_path = ‘’
         #服务器软件sha信息
         self.remote_info_sha = self.get_remote_sha_info(remote_shafile_url)
         #服务器软件日志信息
         self.remote_version,self.update_log = self.get_remote_log_info(remote_logfile_url)
         #zip信息链接
         remote_zipfile_url = f"http://192.168.3.107/tof_measurement_tool_v{self.remote_version}.zip"

         # if self.local_version != self.remote_version:
         # 备份文件
         # self.backup_local_file()
         # 显示日志线程

         self.show_log_thread = show_log_thread()
         self.show_log_thread.update_log = self.update_log
         self.show_log_thread.start()
         self.show_log_thread.update_log_sig.connect(self.show_update_log)
         # 下载软件包
         self.down_load_remote_source(remote_zipfile_url)


    def update_percent(self, msg):
        self.ui.progressBar.setValue(msg)


    def update_speed(self, msg):
        self.ui.speed_label.setText(msg)


    def show_update_log(self, msg):
        # 更新展示
        self.ui.plainTextEdit_change_log.appendPlainText(msg)


    # 获取远程info 信息 下的 sha值
    def get_remote_sha_info(self, url):
        context_res = requests.get(url)
        remote_sha = context_res.json()['sha']
        return remote_sha


    def get_remote_log_info(self, url):
        content = requests.get(url)
        content.encoding = content.apparent_encoding
        content = content.text
        remote_version = content.split('-')[0].split(' ')[-2].replace('[', '').replace(']', '')
        update_log = content.split('\r\n')
        return remote_version, update_log


    def down_load_remote_source(self, url):
        self.down_file_thread = down_file_thread()
        self.down_file_thread.update_percent_sig.connect(self.update_percent)
        self.down_file_thread.update_speed_sig.connect(self.update_speed)
        self.down_file_thread.finished.connect(self.down_load_finished)

        context_res = requests.get(url, stream=True)
        self.context_length = int(context_res.headers['Content-Length'])  # 数据长
        self.file_path = context_res.headers['Content-Disposition'].split("=")[-1].replace('"', "").replace(';', "")
        self.file_type = self.file_path.split('.')[-1]
        self.down_file_thread.path = self.file_path
        self.down_file_thread.context_length = self.context_length
        self.down_file_thread.context_res = context_res
        self.down_file_thread.start()


    def down_load_finished(self):
        # 获取压缩包的sha值
        if self.file_type == "zip":
            sha = hashlib.sha1()
            file_size = os.path.getsize(self.file_path)
            with open(self.file_path, mode='rb') as f:
                while file_size > 1024:
                    content = f.read(1024)
                    sha.update(content)
                    file_size -= 1024
                else:
                    content = f.read(file_size)
                    sha.update(content)
                    file_size = 0
            self.file_sha = sha.hexdigest()

        # 解压zip 包
        if self.file_sha == self.remote_info_sha:
            zip = zipfile.ZipFile(self.file_path, 'r')
            zip.extractall()
            zip.close()

            # 启动应用程序
            path = os.path.join(os.getcwd(), 'tof_measurement_tool.dist\\tof_measurement_tool.exe')
            tof_measurement_tool = subprocess.Popen(path)

            # 删除多余zip 文件
            os.unlink(self.file_path)

            # 关闭主程序
            self.close()
            tof_measurement_tool.wait()


    # 备份旧版本文件
    def backup_local_file(self):
        # 创建备份目录
        backup_path = f'backup_{self.local_version}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
        if os.path.isdir(backup_path):
            pass
        else:
            os.mkdir(backup_path)
            # 移动文件
        for path in os.listdir('.'):
            file = os.path.join('.', path)
            if file.endswith('py'):
                continue
            elif 'backup' in file:
                continue
            elif file.endswith('ui'):
                continue
            else:
                shutil.copy(file, backup_path)

if __name__ == '__main__':
     app = QtWidgets.QApplication(sys.argv)
     app.setStyle(‘QtCurve’)
     gui = update_app()
     gui.show()
     sys.exit(app.exec())'''