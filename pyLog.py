import datetime
import logging
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QTextEdit, QVBoxLayout
from os import path
from dateutil import rrule, parser

now = datetime.datetime.now()  # 获取当前时间
otherStyleTime = now.strftime("%Y-%m-%d")  # "%Y-%m-%d-%H-%M-%S"
user_path = f"{path.expanduser('~')}\\logs"  # 获取用户路径
print(f"user_path:{user_path}")
os.makedirs(user_path, exist_ok=True)  # 获取用户 logs 文件夹  如果不存在则创建文件夹
log_path = f"{user_path}\\{otherStyleTime}.log"  # 以当前日期创建.log日志


def clean_log(cleaningdays=7):
    """
    清理旧日志文件
    :param cleaningdays: 清理几天以上的旧文件。
    :return:
    """

    for f in os.listdir(user_path):  # 遍历 logos文件下的文件
        if f.split(".")[-1] == "log":  # 只取.log的文件
            try:
                start = parser.parse(f, fuzzy=True)  # 开始日期
                end = parser.parse(otherStyleTime, fuzzy=True)  # 今日日期
                days = rrule.rrule(rrule.DAILY, dtstart=start, until=end).count()  # 相差天数
            except:
                continue
            if days > cleaningdays:
                if os.path.exists(f"{user_path}\\{f}"):  # 判断生成的路径对不对，防止报错、
                    os.remove(f"{user_path}\\{f}")  # 删除超过7天的日志


class ConsolePanelHandler(logging.Handler):

    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.parent = parent

    def emit(self, record):
        """输出格式可以按照自己的意思定义HTML格式"""
        record_dict = record.__dict__
        asctime = record_dict['asctime'] + " >> "
        line = record_dict['filename'] + " -> line:" + str(record_dict['lineno']) + " | "
        levelname = record_dict['levelname']
        message = record_dict['message']
        if levelname == 'ERROR':
            color = "#FF0000"
        elif levelname == 'WARNING':
            color = "#FFD700"
        else:
            color = "#008000"
        html = f'''
        <div >
            <span>{asctime}</span>
            <span style="color:#4e4848;">{line.upper()}</span>
            <span style="color: {color};">{levelname}</span>
            <span style="color:	#696969;">{message}</span>
        </div>
        '''
        self.parent.write(html)  # 将日志信息传给父类 write 函数 需要在父类定义一个函数


class Log:
    def __init__(self, ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=20)
        file_log = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s >> (%(filename)s[line:%(lineno)d]) | %(levelname)s: %(message)s - ',
                                      '%Y-%m-%d %H:%M:%S')
        file_log.setFormatter(formatter)
        self.logger.addHandler(file_log)

    def get_log(self):
        return self.logger


logger = Log().get_log()  # 全局能访问


class Main(QWidget):
    def __init__(self, father=None):
        super().__init__(father)
        handler = ConsolePanelHandler(self)  # 初始化日志
        logger.addHandler(handler)  # 声明日志输出
        self.initUI()
        self.serial_dict = {}  # 串口对象字典
        self.com = QSerialPort()  # 串口对象
        self.com.setBaudRate(QSerialPort.Baud115200)  # 设置波特率
        self.get_serial_port()  # 获取串口
        self.combobox.activated[str].connect(self.open_serial_port)  # 选择信号
        self.com.readyRead.connect(self.readSerialPortInfo)  # 接收单片机数据

        logger.info(f"转换后=11111111")
        logger.debug(f"转换后=11111111")
        logger.error(f"转换后=11111111")
    def initUI(self):
        layout = QVBoxLayout(self)
        self.edit = QTextEdit()
        self.edit.setAlignment(Qt.AlignCenter)  # 文本居中
        self.edit.setReadOnly(True)  # 文本内容 只读.不可编辑
        self.edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        self.edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏垂直滚动条

        self.combobox = QComboBox()
        self.combobox.move(100, 100)
        layout.addWidget(self.edit)
        layout.addWidget(self.combobox)

    def write(self, s):
        """日志"""
        self.edit.append(s)
        self.edit.moveCursor(QTextCursor.End)  # 光标末尾
        self.edit.moveCursor(QTextCursor.StartOfLine)  # 光标换行

    def readSerialPortInfo(self):
        print("666666666666666666666")
        """接收单片机数据。单片机有数据发送将会触发此函数"""
        datas = self.com.readAll()
        if not datas.isEmpty():  # 不接收空数据
            self.com.write(bytes.fromhex("4F 4B 21"))  # 发送 OK 数据给单片机，
            data = datas.toHex().toUpper().__str__()[2:-1]  # .toHex()字节码转字符 .toUpper()字符串转大写
            logger.info(f"转换前=={datas}")
            logger.info(f"转换后=={data}")

    def open_serial_port(self, name):
        print("aaaaaaa")
        port_Arduino = QSerialPortInfo(name)
        if port_Arduino.isBusy():  # 检查串口是否被占用
            print("Serial port is occupied")
            return
        try:
            self.com.setPort(self.serial_dict[name])  # 设置串口
            self.com.open(QSerialPort.ReadWrite)  # 打开串口
        except Exception as e:
            print(f"打开失败{e.__str__()}")
            return
        else:
            if self.com.isOpen():  # 判断串口是否打开
                print(f"{name}-串口打开成功...")

    def get_serial_port(self):
        """获取串口"""
        com_list = QSerialPortInfo.availablePorts()
        for com in com_list:
            self.serial_dict[com.portName()] = com  # 将串口对象存储字典 com.portName() 返回串口名
        self.combobox.addItems(list(self.serial_dict.keys()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())