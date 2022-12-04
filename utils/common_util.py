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


# 获取线程数
def get_thread_number(thread_name):
    thread_num = 5
    try:
        if thread_name in os.environ and len(os.environ[thread_name]) > 0:
            thread_num = int(os.environ[thread_name])
            logger.info("获取到线程数: {}".format(thread_num))
        else:
            logger.info("暂未设置线程数，默认数量{}".format(thread_num))
    except Exception:
        logger.info("线程池数量获取出错，设置默认数量{}".format(thread_num))
    return thread_num