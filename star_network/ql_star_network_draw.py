"""
cron: 0 0 1/3 * * ?
new Env('StarNetwork抽奖')
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.common_util import load_file, get_thread_number
from utils.star_network_util import encrypt

thread_name = 'Star_ThreadNum'
file_name = 'StarNetworkToken'
application_name = 'StarNetwork抽奖'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)

running_count = 0
total_count = 0
success_count = 0
libra_fail_email = []
event_fail_email = []


def task(index, email, token, lock):
    logger.info("【{}】正在操作：{}".format(index, email))
    headers = {"User-Agent": "Dart/2.16 (dart:io)", "Authorization": "Bearer {}".format(token)}

    for i in range(0, 3):
        try:
            resp = requests.get('https://api.starnetwork.io/v3/libra/draw', headers=headers, timeout=10)
            break
        except Exception as ex:
            if i != 2:
                logger.info("加速抽奖出错----{}----进行第{}次重试----{}".format(email, i + 1, ex))
            else:
                logger.info("加速抽奖出错----{}----{}次重试完毕----{}".format(email, i + 1, ex))

    for i in range(0, 3):
        try:
            resp = requests.get('https://api.starnetwork.io/v3/auth/user', headers=headers, timeout=10)
            if resp.text.count('{"id":') > 0:
                payload = {"id": resp.json()['id'], "action": "draw_boost"}
                resp = requests.post('https://api.starnetwork.io/v3/event/draw', json=encrypt(payload),
                                     headers=headers, timeout=10)
            break
        except Exception as ex:
            if i != 2:
                logger.info("令牌抽奖出错----{}----进行第{}次重试----{}".format(email, i + 1, ex))
            else:
                logger.info("令牌抽奖出错----{}----{}次重试完毕----{}".format(email, i + 1, ex))

    lock.acquire()
    global running_count
    running_count = running_count - 1
    lock.release()


if __name__ == '__main__':
    logger.info("=====开始执行读取文本=====")
    lines = load_file(file_name)
    logger.info("=====读取文本执行完毕=====\n")

    logger.info("=====开始执行抽奖任务=====")
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
            logger.error("数据: {}，Token读取失败，错误: {}".format(line, e))
    pool.shutdown()
    logger.info("=====抽奖任务执行完毕=====\n")
