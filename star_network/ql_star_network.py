"""
cron: 0 0 2,14 * * ?
new Env('StarNetwork养号')
"""

import hashlib
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.common_util import load_file, get_thread_number
from notify import send

file_name = 'StarNetwork'
thread_name = 'Star_ThreadNum'
application_name = 'StarNetwork养号'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(lineno)d %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)

total_count = 0
login_fail_msg = []
start_fail_msg = []
sign_fail_msg = []
signing_msg = []


def encrypt(payload):
    timestamp = int(time.time() * 1000)
    data = (str(payload) + ':D7C92C3FDB52D54147B668DC6F8A5@' + str(timestamp)).replace("'", '"').encode()
    sign = hashlib.md5(data).hexdigest()
    payload['timestamp'] = timestamp
    payload['hash'] = sign
    return payload


class StarNetwork(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.headers = {"User-Agent": "Dart/2.16 (dart:io)"}
        self.message = ''
        self.error_msg = ''

    def login(self):
        payload = {"email": self.email, "password": self.password}
        try:
            res = requests.post("https://api.starnetwork.io/v1/email/login", json=encrypt(payload))
            if res.text.count('jwt') > 0:
                token = res.json()['jwt']
                self.headers['Authorization'] = "Bearer {}".format(token)
                logger.info("登录成功----{}".format(self.email))
            else:
                login_fail_msg.append('登录失败----{}----{}'.format(self.email, res.text))
            return res.text.count('jwt') > 0
        except Exception as ex:
            login_fail_msg.append('登录失败----{}----{}'.format(self.email, ex))

    def start(self):
        try:
            res = requests.post("https://api.starnetwork.io/v1/session/start", headers=self.headers)
            if res.text.count('endAt') > 0:
                logger.info("挖矿成功----{}".format(self.email))
            else:
                start_fail_msg.append('挖矿失败----{}----{}'.format(self.email, res.text))
            return res.text.count('endAt') > 0
        except Exception as ex:
            start_fail_msg.append('挖矿失败----{}----{}'.format(self.email, ex))

    def sign(self):
        try:
            res = requests.post('https://api.starnetwork.io/v3/user/checkin', headers=self.headers)
            if res.text.count('CLAIMED') > 0:
                logger.info("签到成功----{}".format(self.email))
            else:
                res = requests.get('https://api.starnetwork.io/v3/user/checkin', headers=self.headers)
                if res.json()['checkins'][0] is not None and res.json()['checkins'][0] != '':
                    signing_msg.append("未到签到时间----{}".format(self.email))
                else:
                    sign_fail_msg.append("签到失败----{}----{}".format(self.email, res.text))
        except Exception as ex:
            sign_fail_msg.append("签到失败----{}----{}".format(self.email, ex))

    def draw(self):
        try:
            res = requests.get('https://api.starnetwork.io/v3/libra/draw', headers=self.headers)
        except Exception as ex:
            logger.error("{}----加速抽奖出错----{}".format(self.email, ex))
        try:
            res = requests.get('https://api.starnetwork.io/v3/auth/user', headers=self.headers)
            if res.text.count('{"id":') > 0:
                payload = {"id": res.json()['id'], "action": "draw_boost"}
                res = requests.post('https://api.starnetwork.io/v3/event/draw', json=encrypt(payload),
                                    headers=self.headers)
        except Exception as ex:
            logger.error("{}----令牌抽奖出错----{}".format(self.email, ex))


def task(star_network):
    if star_network.login():
        star_network.start()
        star_network.sign()
        star_network.draw()


if __name__ == '__main__':
    lines = load_file(file_name)
    thread_num = get_thread_number(thread_name)
    if thread_num > len(lines):
        thread_num = len(lines)
    if thread_num < 1:
        thread_num = 1

    pool = ThreadPoolExecutor(max_workers=thread_num)
    for line in lines:
        line = line.strip()
        try:
            split = line.split('----')
            email = split[0]
            password = split[1]
            star = StarNetwork(email, password)
            thread = pool.submit(task, star)
        except Exception as e:
            login_fail_msg.append("数据: {}，账号密码读取失败，错误: {}".format(line, e))
    pool.shutdown()

    if len(login_fail_msg) > 0:
        logger.info("登录失败：")
        for msg in login_fail_msg:
            logger.error(msg)

    if len(start_fail_msg) > 0:
        logger.info("挖矿失败：")
        for msg in start_fail_msg:
            logger.error(msg)

    if len(sign_fail_msg) > 0:
        logger.info("签到失败：")
        for msg in sign_fail_msg:
            logger.error(msg)

    if len(signing_msg) > 0:
        logger.info("未到签到时间：")
        for msg in signing_msg:
            logger.error(msg)

    send(application_name, '账号总数: {}\n登录失败数: {}\n挖矿失败数: {}\n签到失败数: {}\n未到签到时间数: {}'.format(len(lines),
                                                                                           len(login_fail_msg),
                                                                                           len(start_fail_msg),
                                                                                           len(sign_fail_msg),
                                                                                           len(signing_msg)))
