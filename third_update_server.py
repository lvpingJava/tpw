import os
from flask import Flask, send_file

n_version = '1.5.3'
app = Flask(__name__)
# 版本查询
@app.route('/version', methods=['GET'])
def get_version():
    return n_version


# http://192.168.71.27:80/version
# 获取最新文件
@app.route('/update/app', methods=['GET'])
def update_app():
    # 新版本文件路径
    file_path = "I:/tpwVer.zip"
    return send_file(file_path)


if __name__ == '__main__':
    app.run(host='127.0.0.0', port=5555)

