import logging

import datetime
logger = logging.getLogger(__name__)
class Log:
    def __init__(self, ):
        self.logger = logger
        logging.basicConfig(level="INFO")
        #self.logger.setLevel(level=20)

        # 设置日志等级
        self.logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()  # 获取当前时间
        otherStyleTime = now.strftime("%Y-%m-%d")  # "%Y-%m-%d-%H-%M-%S"
        # 追加写入文件a ，设置utf-8编码防止中文写入乱码
        file_log = logging.FileHandler(f'./log/{otherStyleTime}.log', 'a', encoding='utf-8')

        # 向文件输出的日志级别
        file_log.setLevel(logging.DEBUG)

        # 向文件输出的日志信息格式
        formatter = logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s -%(process)s')
        file_log.setFormatter(formatter)
        # 加载文件到logger对象中
        self.logger.addHandler(file_log)

        #控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level="WARNING")
        console_fmt = "%(name)s--->%(levelname)s--->%(asctime)s--->%(message)s--->%(lineno)d"
        fmt1 = logging.Formatter(fmt=console_fmt)
        console_handler.setFormatter(fmt=fmt1)
        # 第五步：将控制台
        self.logger.addHandler(console_handler)


    def get_log(self):
        return self.logger




if __name__ == "__main__":
    logger = Log().get_log()  # 全局能访问
    logger.debug('----调试信息 [debug]------')
    logger.info('[info]')
    logger.warning('警告信息[warning]')
    logger.error('错误信息[error]')
    logger.critical('严重错误信息[crtical]')