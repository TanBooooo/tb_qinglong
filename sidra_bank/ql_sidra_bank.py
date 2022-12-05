"""
cron: 0 0 4,16 * * ?
new Env('SidraBank养号')
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

from notify import send
from utils.common_util import load_file, get_thread_number

file_name = 'SidraBank'
thread_name = 'Sidra_ThreadNum'
application_name = 'SidraBank养号'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(lineno)d %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)
success_count = 0
error_count = 0
error_email = []


class sidra_bank(object):
    def __init__(self, email, token):
        self.email = email
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            "Authorization": "Bearer " + token
        }
        self.blockchain_id = ''
        self.error_msg = ''
        self.success = False

    def get_id(self):
        while True:
            res = requests.get("https://www.minesidra.com/api/blockchain/mine/request/", headers=self.headers)
            if res.text.count('success'):
                self.blockchain_id = res.json()['data']['id']
                break
            if res.text.count('status') > 0 and res.json()['data']['last_click'] is not None:
                self.error_msg = '当前正在挖矿----{}'.format(self.email)
            elif res.text.count('code') > 0 or res.text.count('code') == 'token_not_valid':
                self.error_msg = 'Token失效----{}'.format(self.email)
            elif res.text.count('status') == 0 or res.text.count('status') != 'busy':
                self.error_msg = '未知错误----{}----{}'.format(self.email, res.text)
            if self.error_msg != '':
                logger.error(self.error_msg)
                break

        if self.blockchain_id == '' and self.error_msg == '':
            self.error_msg = 'ID获取失败----{}----{}'.format(self.email, res.text)
            logger.error(self.error_msg)

    def start(self):
        if self.blockchain_id != '':
            payload = {"type": 2, "data": {"id": self.blockchain_id}}
            res = requests.post("https://www.minesidra.com/api/blockchain/mine/submit/", json=payload,
                                headers=self.headers)
            if res.text.count('status') > 0 or res.json()['status'] == 'success':
                logger.info('挖矿成功----{}'.format(self.email))
                self.success = True
            else:
                self.error_msg = '挖矿失败----{}----{}'.format(self.email, res.text)
                logger.error(self.error_msg)


def task(sidra, lock):
    sidra.get_id()
    sidra.start()
    lock.acquire()
    if sidra.success:
        global success_count
        success_count = success_count + 1
    else:
        global error_count
        global error_email
        error_count = error_count + 1
        error_email.append(sidra.error_msg)
    lock.release()


if __name__ == '__main__':
    lines = load_file(file_name)
    thread_num = get_thread_number(thread_name)
    if thread_num > len(lines):
        thread_num = len(lines)
    if thread_num < 1:
        thread_num = 1

    lock = threading.RLock()
    pool = ThreadPoolExecutor(max_workers=thread_num)
    for line in lines:
        line = line.strip()
        try:
            split = line.split('----')
            email = split[0]
            token = split[1]
            sidra = sidra_bank(email, token)
            thread = pool.submit(task, sidra, lock)
        except Exception:
            error_count = error_count + 1
            error_email.append("数据:{}，账号密码读取失败".format(line))
    pool.shutdown()

    if len(error_email) > 0:
        logger.error("失败统计: ")
        for em in error_email:
            logger.error(em)

    logger.info('总计成功数: {}'.format(success_count))
    logger.info('总计失败数: {}'.format(error_count))
    send(application_name, '总计成功数: {}\n总计失败数: {}'.format(success_count, error_count))
