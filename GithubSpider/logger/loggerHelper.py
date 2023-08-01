import logging
import datetime
import os

def loggingconfig():
    log_filename = datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S.log")  # 根据当前时间生成日志文件名
    log_dir = "./logs/"  # 指定日志目录

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    print("Log_dir : " + log_dir)
    log_file = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s ',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')  # 输出到文件
        ]
    )