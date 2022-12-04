"""
cron: 0 0 2,14 * * ?
new Env('StarNetwork养号')
"""

import hashlib
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from common_util import load_file, pushplus_send, get_thread_number

file_name = 'StarNetwork'
thread_name = 'Star_ThreadNum'
application_name = 'StarNetwork养号'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(lineno)d %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)
success_count = 0
error_count = 0
error_email = []


def encrypt(payload):
    timestamp = int(time.time() * 1000)
    sign = hashlib.md5(
        (str(payload) + ':D7C92C3FDB52D54147B668DC6F8A5@' + str(timestamp)).replace("'", '"').encode()).hexdigest()
    payload['timestamp'] = timestamp
    payload['hash'] = sign
    return payload


class StarNetwork(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.headers = {"User-Agent": "Dart/2.16 (dart:io)"}
        self.error_msg = ''
        self.success = False

    def login(self):
        payload = {"email": self.email, "password": self.password}
        res = requests.post("https://api.starnetwork.io/v1/email/login", json=encrypt(payload))
        if res.text.count('jwt') > 0:
            token = res.json()['jwt']
            self.headers['Authorization'] = "Bearer {}".format(token)
            logger.info('登录成功----{}'.format(self.email))
        else:
            self.error_msg = '登录失败----{}----{}'.format(self.email, res.text)
            logger.error(self.error_msg)

        return res.text.count('jwt') > 0

    def start(self):
        res = requests.post("https://api.starnetwork.io/v1/session/start", headers=self.headers)
        if res.text.count('endAt') > 0:
            logger.info("挖矿成功----{}".format(self.email))
            self.success = True
        else:
            self.error_msg = '挖矿失败----{}----{}'.format(self.email, res.text)
            logger.error(self.error_msg)
        return res.text.count('endAt') > 0

    def draw(self):
        requests.get('https://api.starnetwork.io/v3/libra/draw', headers=self.headers)
        res = requests.get('https://api.starnetwork.io/v3/auth/user', headers=self.headers)
        if res.text.count('id') > 0:
            payload = {"id": res.json()['id'], "action": "draw_boost"}
            requests.post('https://api.starnetwork.io/v3/event/draw', json=encrypt(payload), headers=self.headers)


def task(star, lock):
    if star.login():
        star.start()
        star.draw()
    lock.acquire()
    if star.success:
        global success_count
        success_count = success_count + 1
    else:
        global error_count
        global error_email
        error_count = error_count + 1
        error_email.append(star.error_msg)
    lock.release()


if __name__ == '__main__':
    lines = load_file(file_name)
    thread_num = get_thread_number(thread_name)
    if thread_num > len(lines):
        thread_num = len(lines)

    lock = threading.RLock()
    pool = ThreadPoolExecutor(max_workers=thread_num)
    for line in lines:
        line = line.strip()
        try:
            split = line.split('----')
            email = split[0]
            password = split[1]
            star = StarNetwork(email, password)
            thread = pool.submit(task, star, lock)
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
    if "PUSH_PLUS_TOKEN" in os.environ and len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
        pushplus_send(application_name, '总计成功数: {}\n总计失败数: {}'.format(success_count, error_count),
                      os.environ["PUSH_PLUS_TOKEN"])