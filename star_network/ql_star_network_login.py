"""
cron: 0 0 0 * * ?
new Env('StarNetwork登录')
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.common_util import load_file, get_thread_number, write_file, del_file
from notify import send
from utils.star_network_util import encrypt

thread_name = 'Star_ThreadNum'
file_name = 'StarNetwork'
application_name = 'StarNetwork登录'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)

running_count = 0
total_count = 0
success_email = []
blocked_email = []
fail_email = []


def task(index, email, password, lock):
    logger.info("【{}】正在操作：{}".format(index, email))
    headers = {"User-Agent": "Dart/2.16 (dart:io)"}
    payload = encrypt({"email": email, "password": password})
    resp = None
    exception = None
    for i in range(0, 3):
        try:
            resp = requests.post("https://api.starnetwork.io/v1/email/login", json=payload, headers=headers, timeout=10)
            if resp.text.count('jwt') > 0:
                if resp.json()['status'] == 'registered':
                    token = resp.json()['jwt']
                    success_email.append("{}----{}----{}".format(email, password, token))
                if resp.json()['status'] == 'blocked':
                    blocked_email.append('{}----{}'.format(email, password))
            else:
                fail_email.append('{}----{}----{}'.format(email, password, resp.text))
            break
        except Exception as ex:
            if i != 2:
                logger.info("登录出错----{}----进行第{}次重试----{}".format(email, i + 1, ex))
            else:
                logger.info("登录出错----{}----{}次重试完毕----{}".format(email, i + 1, ex))
                exception = ex
    if resp is None:
        fail_email.append('{}----{}----{}'.format(email, password, exception))

    lock.acquire()
    global running_count
    running_count = running_count - 1
    lock.release()


if __name__ == '__main__':
    logger.info("=====开始执行读取文本=====")
    lines = load_file(file_name)
    del_file(file_name + 'Token')
    logger.info("=====读取文本执行完毕=====\n")

    logger.info("=====开始执行登录任务=====")
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
            password = split[1]
            thread = pool.submit(task, index, email, password, lock)
            running_count = running_count + 1
            while True:
                time.sleep(0.05)
                if running_count < thread_num:
                    break
        except Exception as e:
            fail_email.append("数据: {}，账号密码读取失败，错误: {}".format(line, e))
    pool.shutdown()
    logger.info("=====登录任务执行完毕=====\n")

    if len(blocked_email) > 0 or len(fail_email) > 0:
        logger.info("=====开始执行统计任务=====")
        if len(blocked_email) > 0:
            logger.error("封禁账号列表：")
            for email in blocked_email:
                logger.error(email)

        if len(fail_email) > 0:
            logger.error("登录失败列表：")
            for email in fail_email:
                logger.error(email)
        logger.info("=====统计任务执行完毕=====\n")

    logger.info("=====开始执行保存文本====")
    if len(success_email) > 0:
        logger.info("-----开始保存成功文本-----")
        success_text = ''
        token_text = ''
        for email in success_email:
            token_text = token_text + email + '\n'
            res = email.split('----')
            success_text = success_text + res[0] + '----' + res[1] + '\n'
        write_file(file_name, success_text)
        write_file(file_name + 'Token', token_text)
        logger.info("-----成功文本保存完毕-----")
    if len(blocked_email) > 0:
        logger.info("-----开始保存封禁文本-----")
        blocked_text = ''
        for email in blocked_email:
            blocked_text = blocked_text + email + '\n'
        write_file(file_name + '已封禁', blocked_text)
        logger.info("-----封禁文本保存完毕-----")
    if len(fail_email) > 0:
        logger.info("-----开始保存失败文本-----")
        fail_text = ''
        for email in fail_email:
            fail_text = fail_text + email + '\n'
        write_file(file_name + '登录失败', fail_text)
        logger.info("-----失败文本保存完毕-----")
    logger.info("=====保存文本执行完毕====\n")

    logger.info("=====开始执行推送任务=====")
    send(application_name, '账号总数: {}\n登录成功数: {}\n账号封禁数: {}\n登录失败数: {}'.format(len(lines),
                                                                              len(success_email),
                                                                              len(blocked_email),
                                                                              len(fail_email)))
    logger.info("=====推送任务执行完毕=====\n")
