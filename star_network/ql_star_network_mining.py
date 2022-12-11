"""
cron: 0 0 1/12 * * ?
new Env('StarNetwork挖矿')
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.common_util import load_file, get_thread_number
from notify import send

thread_name = 'Star_ThreadNum'
file_name = 'StarNetworkToken'
application_name = 'StarNetwork挖矿'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)

running_count = 0
total_count = 0
success_count = 0
fail_email = []


def task(index, email, token, lock):
    logger.info("【{}】正在操作：{}".format(index, email))
    headers = {"User-Agent": "Dart/2.16 (dart:io)", "Authorization": "Bearer {}".format(token)}
    resp = None
    exception = None
    for i in range(0, 3):
        try:
            resp = requests.post("https://api.starnetwork.io/v1/session/start", headers=headers, timeout=10)
            if resp.text.count('endAt') == 0:
                fail_email.append('挖矿失败----{}----{}'.format(email, resp.text))
            else:
                global success_count
                success_count = success_count + 1
            break
        except Exception as ex:
            if i != 2:
                logger.info("挖矿出错----{}----进行第{}次重试----{}".format(email, i + 1, ex))
            else:
                logger.info("挖矿出错----{}----{}次重试完毕----{}".format(email, i + 1, ex))
                exception = ex
    if resp is None:
        fail_email.append('挖矿失败----{}----{}'.format(email, exception))

    lock.acquire()
    global running_count
    running_count = running_count - 1
    lock.release()


if __name__ == '__main__':
    logger.info("=====开始执行读取文本=====")
    lines = load_file(file_name)
    logger.info("=====读取文本执行完毕=====\n")

    logger.info("=====开始执行挖矿任务=====")
    thread_num = get_thread_number(thread_name, len(lines))
    lock = threading.RLock()
    pool = ThreadPoolExecutor(max_workers=thread_num)
    index = 0
    for line in lines:
        index = index + 1
        line = line.strip()
        try:
            split = line.split('----')
            email = split[0]
            token = split[2]
            thread = pool.submit(task, index, email, token, lock)
            running_count = running_count + 1
            while True:
                time.sleep(0.05)
                if running_count < thread_num:
                    break
        except Exception as e:
            fail_email.append("数据: {}，Token读取失败，错误: {}".format(line, e))
    pool.shutdown()
    logger.info("=====挖矿任务执行完毕=====\n")

    if len(fail_email) > 0:
        if len(fail_email) > 0:
            logger.error("登录失败列表：")
            for email in fail_email:
                logger.error(email)
        logger.info("=====统计任务执行完毕=====\n")

    logger.info("=====开始执行推送任务=====")
    send(application_name, 'Token总数: {}\n挖矿成功数: {}\n挖矿失败数: {}'.format(len(lines),
                                                                      success_count,
                                                                      len(fail_email)))
    logger.info("=====推送任务执行完毕=====\n")
