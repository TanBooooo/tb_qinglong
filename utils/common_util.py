import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(lineno)d %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger('通用工具')


# 读取文本
def load_file(file_name):
    count = 0
    lines = []
    logger.info("正在读取{}文本信息".format(file_name))
    with open(sys.path[0] + "/" + file_name + ".txt", "r+") as f:
        while True:
            line = f.readline().strip()
            if line is None or line == '':
                break
            count = count + 1
            lines.append(line)
    logger.info("读取完毕，总计数量: {}".format(count))
    return lines


# 读取文本
def write_file(file_name, text, append = False):
    mode = 'w+'
    if append:
        mode = 'a+'
    with open(sys.path[0] + "/" + file_name + ".txt", mode) as f:
        f.write(text)


# 获取线程数
def get_thread_number(thread_name, size):
    thread_num = 5
    try:
        if thread_name in os.environ and len(os.environ[thread_name]) > 0:
            thread_num = int(os.environ[thread_name])
            logger.info("获取到线程数: {}".format(thread_num))
        else:
            logger.info("暂未设置线程数，默认数量{}".format(thread_num))
    except Exception:
        logger.info("线程池数量获取出错，设置默认数量{}".format(thread_num))

    if thread_num > size:
        thread_num = size
        logger.info("线程数量大于文本数量，设置文本数量{}".format(size))

    if thread_num < 1:
        thread_num = 1
        logger.info("线程数量不能小于0，设置默认数量1")

    return thread_num
