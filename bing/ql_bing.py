"""
cron: 0 0 0/4 * * ?
new Env('StarNetwork养号')
"""

import logging
import random
import re
import string
from urllib import parse

import requests

file_name = 'Bing'
thread_name = 'Bing'
application_name = 'Bing搜索'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(lineno)d %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(application_name)


def random_unicode():
    value = ''
    for i in range(0, random.randint(5, 10)):
        value = value + random.choice(string.ascii_letters)
    return value


class Bing(object):
    def __init__(self, cookies):
        self.cookies = cookies
        self.headers = {
            'Cookie': 'MUID=086CAF441A786AE609ACBE211B486B54; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=3772D997A72047FFBF661272408604EA&dmnchg=1; MUIDB=086CAF441A786AE609ACBE211B486B54; _EDGE_S=SID=1F2F735E09346DAB18F1612D08776C88; ZHCHATSTRONGATTRACT=TRUE; ipv6=hit=1670403331193&t=4; CSRFCookie=5adda01d-16bb-42f7-aeda-4535eb9f2434; SRCHUSR=DOB=20220411&T=1670399726000&TPC=1670399729000; ANON=A=BD6C4FF729F6B2890C988DA7FFFFFFFF&E=1bb7&W=2; NAP=V=1.9&E=1b5d&C=JaE5hdB1_XWx2rv71pDDsZZQpJwCcMCwGpFNChu8e3DrscqoNMGpCw&W=1; PPLState=1; KievRPSSecAuth=FABKBBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACGZqveR9UbtECASY/HNs2zu3gnQAeKggUoJpPJb1HqBewODEVGlmRgRM9wE+tBvjY+DgYZSM5sHGUf+xsblsQw0GV0Y6KkoS9m8wpxELjRXj6qASQ4opsEdKG+NpRzbmp6E9DAsZsBvnK/evIpo1t/MNkpMyDWooVBUxuM9woQJjffbJAD/dJGgV1VAhpRgAhxvAvewjpWlMM/6rmC71FivTW2NS8UlwSbpFR+818BEhJg1RiK244mGL+B29RgR8UDjUMoM0/ldcwj4fa//TqZHKLdSQO+QrUbreFumN9khmokI7wpJKaeO72RTWg7Wm01zBLSy1s/RFpw892UFvgzM1dtngeQKdYqFvJP+CbdATyWnRB6zGZM6vchMFghZEFq89gVbd03t2aL/VDvBUyBfUhGkCxzDsAfPy282qXpVC0LFDyawWFkj3RPGIfRyyR/xGokvqZPFNCP4pP1NvB1+E0JG206jTSG6hQRUhHq7HtgR60LyeUSt1OTGOOFlUx0i6j9k1ZMoAmiUUPJ3LMtzG7WpouzPWDmymHaWTrpl/AAb6lkICyeLMHVZOMSNBYEwb9t96F6YsZCGL2DtCo70ZPEst3Sxs/f75jJeo3LB5GYNAcIYUIMVKVtF7PekNrRqOXu4SNeJ1Ih4HWRu6t/BeZowPjNH3N9z/tpPo9asLlW8TYzqoedgWanMC+0qCDF0hGtQ1oLlsrBxT5Sf8eRGjSNflUcUGPX/HeVCP29GTTDB4RyxekCn7dLlajNUFle0+0u7oVgxtSObOn/Wl2Ie3ierP2vS0AO0uByLaE8uajEWi+trBv5wU4AA6jI0pc8WLi15beihwqn4a7gm7MPUWWLCjUYonkezy6IjcpVQT0Sh9v9UYGbVrTvtvCAwxojE2IiOt7Zka9gF9H9WQk31IyT8KM/0sflkmMLkXp4u2KXublIP2+I64qGe12G3RQ0NuH6hHzpZjFF9HHf/xUpWCOs6tR00j133Ng/DFc88uKCu1l8hxdYsjBj+PJcRYqEasJFyo+ynLHRMWzKYjwwrBP1jWhsgI7Fr/uVNEYQJDKkTHqcU4UFZCRtgepKBpgsVYsld6YgigxtWUK14aVHw7SbNyMgKPmRW5goJUl0oNZSXUR+k267/gzp260IdP/SU5CGoikLkWrq7RdoX3grOGWR1hFZggpg7vTE3uNxJHW3P7O7IFG/hq7mXW3ficjYsLaZJp1b10S7cDyfWU87zWfR49Zlq8qAWFoDTL2pnYQ1dZXIZkK2g6zSaX7u8hhRr2REd4HE7BDcl6U0WtOpXFi2YBLlzE7UFZIgQ8l5pWFUoZnpPyD8vcxtyotVf/yafmOK3t8C5sKmnw/GQ4EceYF7Y+Tw931XuiXhkhdJUWQRsUAI+coRZ69zvi1PcQCnB0OOBb+BFK; _U=1bZ-cB5n_sqn-T-JK21455zzYc5H-HOPNb97meW9vATQsCAAWzDQn8ozVsUVj_hm6YeuLvzX-15KjciUDMOxf4r7D0EytYLieUn-guOfRBHWV0wNAu55wWdPKpxtMzC5NP9Vnah4DyUZUNiA7bOty4GCZvlheDbLaSR4kMQIMrZFv6CdVjov8rVhOnMi6xBjE; WLS=C=debac9b6d2dc8a8f&N=%e5%8d%9a; WLID=n/YIluL8EcwrJ6LFGxWpeuoVXCZzklvO+kqAZmetbemgAd0AN8VYEPa6UDlHezwbezOfg33XgPx/fDnAJ6zqmsxaX5s70DCdDcsm57drQDE=; SUID=A; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=M&BRH=M&CW=1336&CH=864&SW=2560&SH=1440&DPR=1.3&UTC=480&DM=1&HV=1670399887&WTS=63801079296&PV=15.0.0&BZA=0&PRVCW=1336&PRVCH=864&SCW=1319&SCH=2731; _SS=SID=1F2F735E09346DAB18F1612D08776C88&R=11&RB=11&GB=0&RG=1500&RP=11; ZHCHATWEAKATTRACT=TRUE; _RwBf=ilt=1&ihpd=0&ispd=1&rc=11&rb=11&gb=0&rg=1500&pc=11&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=4&l=2022-12-06T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=None&c=MA13C5&t=3067&s=2022-12-07T07:17:35.0630167+00:00&ts=2022-12-07T07:58:04.9206482+00:00&rwred=0&mta=0&e=-sMyQbg-ClDevyBg9fdyfSF_TFaAMcv6Vpl-INv7ZHqUsK8rfSNONSOTyMZKoHPfBsKckJFlLjTPix-6ya--Qg&A=BD6C4FF729F6B2890C988DA7FFFFFFFF; SNRHOP=I=&TS=',
            'Host': 'cn.bing.com',
            'Referer': 'https://cn.bing.com/search?q=wuqi&qs=n&form=QBRE&sp=-1&pq=wuqi&sc=10-4&sk=&cvid=CC5CA84E961341A8AFD8A74590706938&ghsh=0&ghacc=0&ghpl=',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.42'
        }
        self.message = ''
        self.error_msg = ''

    def search(self):
        q = random_unicode()
        url = 'https://cn.bing.com/search?q=' + q + '&aqs=edge..69i57.14983j0j1&pglt=129&FORM=ANCMS9&PC=EDGEDB'
        params = {'q': q, 'ags': 'edge..69i57.14983j0j1', 'pglt': '129', 'FORM': 'ANCMS9', 'PC': 'EDGEDB'}
        data = 'url=' + parse.unquote(url) + '&V=web'
        res = requests.post(url=url, params=params, data=data.encode('utf-8'), headers=self.headers)
        ig = re.findall(',IG:"(.*?)"', res.text)[0]

        url = 'https://cn.bing.com/rewardsapp/ncheader?ver=32827440&IID=SERP.5043&IG=' + ig
        data = 'wb=1;i=1;v=1'
        res = requests.post(url=url, params=params, data=data.encode('utf-8'), headers=self.headers)

        url = 'https://cn.bing.com/rewardsapp/reportActivity?IG=' + ig + '&IID=SERP.5052&q=' + parse.unquote(
            q) + '&aqs=edge..69i57.14983j0j1&pglt=129&FORM=ANCMS9&PC=EDGEDB'
        data = 'url=' + parse.unquote(url) + '&V=web'
        res = requests.post(url=url, params=params, data=data.encode('utf-8'), headers=self.headers)
        logger.info(res.text)


def task(cookies):
    bing = Bing(cookies)
    bing.search()


if __name__ == '__main__':
    # lines = load_file(file_name)
    # thread_num = get_thread_number(thread_name)
    # if thread_num > len(lines):
    #     thread_num = len(lines)
    # if thread_num < 1:
    #     thread_num = 1

    # for line in lines:
    #     line = line.strip()
    #     try:
    #         split = line.split('----')
    #         email = split[0]
    #         password = split[1]
    #         bing = Bing(email)
    #         thread = pool.submit(task, bing)
    #     except Exception as e:
    #         pass
    # pool = ThreadPoolExecutor(max_workers=1)
    # thread = pool.submit(task, 'CSRFCookie=be8aca9f-bec5-45b3-9768-cca572c24ced')
    # pool.shutdown()
    task('MUID=086CAF441A786AE609ACBE211B486B54; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=3772D997A72047FFBF661272408604EA&dmnchg=1; MUIDB=086CAF441A786AE609ACBE211B486B54; _EDGE_S=SID=1F2F735E09346DAB18F1612D08776C88; ZHCHATSTRONGATTRACT=TRUE; ipv6=hit=1670403331193&t=4; CSRFCookie=5adda01d-16bb-42f7-aeda-4535eb9f2434; SRCHUSR=DOB=20220411&T=1670399726000&TPC=1670399729000; ANON=A=BD6C4FF729F6B2890C988DA7FFFFFFFF&E=1bb7&W=2; NAP=V=1.9&E=1b5d&C=JaE5hdB1_XWx2rv71pDDsZZQpJwCcMCwGpFNChu8e3DrscqoNMGpCw&W=1; PPLState=1; KievRPSSecAuth=FABKBBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACGZqveR9UbtECASY/HNs2zu3gnQAeKggUoJpPJb1HqBewODEVGlmRgRM9wE+tBvjY+DgYZSM5sHGUf+xsblsQw0GV0Y6KkoS9m8wpxELjRXj6qASQ4opsEdKG+NpRzbmp6E9DAsZsBvnK/evIpo1t/MNkpMyDWooVBUxuM9woQJjffbJAD/dJGgV1VAhpRgAhxvAvewjpWlMM/6rmC71FivTW2NS8UlwSbpFR+818BEhJg1RiK244mGL+B29RgR8UDjUMoM0/ldcwj4fa//TqZHKLdSQO+QrUbreFumN9khmokI7wpJKaeO72RTWg7Wm01zBLSy1s/RFpw892UFvgzM1dtngeQKdYqFvJP+CbdATyWnRB6zGZM6vchMFghZEFq89gVbd03t2aL/VDvBUyBfUhGkCxzDsAfPy282qXpVC0LFDyawWFkj3RPGIfRyyR/xGokvqZPFNCP4pP1NvB1+E0JG206jTSG6hQRUhHq7HtgR60LyeUSt1OTGOOFlUx0i6j9k1ZMoAmiUUPJ3LMtzG7WpouzPWDmymHaWTrpl/AAb6lkICyeLMHVZOMSNBYEwb9t96F6YsZCGL2DtCo70ZPEst3Sxs/f75jJeo3LB5GYNAcIYUIMVKVtF7PekNrRqOXu4SNeJ1Ih4HWRu6t/BeZowPjNH3N9z/tpPo9asLlW8TYzqoedgWanMC+0qCDF0hGtQ1oLlsrBxT5Sf8eRGjSNflUcUGPX/HeVCP29GTTDB4RyxekCn7dLlajNUFle0+0u7oVgxtSObOn/Wl2Ie3ierP2vS0AO0uByLaE8uajEWi+trBv5wU4AA6jI0pc8WLi15beihwqn4a7gm7MPUWWLCjUYonkezy6IjcpVQT0Sh9v9UYGbVrTvtvCAwxojE2IiOt7Zka9gF9H9WQk31IyT8KM/0sflkmMLkXp4u2KXublIP2+I64qGe12G3RQ0NuH6hHzpZjFF9HHf/xUpWCOs6tR00j133Ng/DFc88uKCu1l8hxdYsjBj+PJcRYqEasJFyo+ynLHRMWzKYjwwrBP1jWhsgI7Fr/uVNEYQJDKkTHqcU4UFZCRtgepKBpgsVYsld6YgigxtWUK14aVHw7SbNyMgKPmRW5goJUl0oNZSXUR+k267/gzp260IdP/SU5CGoikLkWrq7RdoX3grOGWR1hFZggpg7vTE3uNxJHW3P7O7IFG/hq7mXW3ficjYsLaZJp1b10S7cDyfWU87zWfR49Zlq8qAWFoDTL2pnYQ1dZXIZkK2g6zSaX7u8hhRr2REd4HE7BDcl6U0WtOpXFi2YBLlzE7UFZIgQ8l5pWFUoZnpPyD8vcxtyotVf/yafmOK3t8C5sKmnw/GQ4EceYF7Y+Tw931XuiXhkhdJUWQRsUAI+coRZ69zvi1PcQCnB0OOBb+BFK; _U=1bZ-cB5n_sqn-T-JK21455zzYc5H-HOPNb97meW9vATQsCAAWzDQn8ozVsUVj_hm6YeuLvzX-15KjciUDMOxf4r7D0EytYLieUn-guOfRBHWV0wNAu55wWdPKpxtMzC5NP9Vnah4DyUZUNiA7bOty4GCZvlheDbLaSR4kMQIMrZFv6CdVjov8rVhOnMi6xBjE; WLS=C=debac9b6d2dc8a8f&N=%e5%8d%9a; WLID=n/YIluL8EcwrJ6LFGxWpeuoVXCZzklvO+kqAZmetbemgAd0AN8VYEPa6UDlHezwbezOfg33XgPx/fDnAJ6zqmsxaX5s70DCdDcsm57drQDE=; SUID=A; SRCHHPGUSR=SRCHLANG=zh-Hans&BRW=M&BRH=M&CW=1336&CH=864&SW=2560&SH=1440&DPR=1.3&UTC=480&DM=1&HV=1670399800&WTS=63801079296&PV=15.0.0&BZA=0&PRVCW=1336&PRVCH=819&SCW=1319&SCH=2323; _SS=SID=1F2F735E09346DAB18F1612D08776C88&R=8&RB=8&GB=0&RG=1500&RP=3; _RwBf=ilt=1&ihpd=0&ispd=1&rc=8&rb=8&gb=0&rg=1500&pc=3&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=2&l=2022-12-06T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=None&c=MA13C5&t=3067&s=2022-12-07T07:17:35.0630167+00:00&ts=2022-12-07T07:56:37.5754953+00:00&rwred=0&mta=0&e=-sMyQbg-ClDevyBg9fdyfSF_TFaAMcv6Vpl-INv7ZHqUsK8rfSNONSOTyMZKoHPfBsKckJFlLjTPix-6ya--Qg&A=BD6C4FF729F6B2890C988DA7FFFFFFFF; SNRHOP=I=&TS=')
    # send(application_name, '账号总数: {}\n登录失败数: {}\n挖矿失败数: {}\n签到失败数: {}\n未到签到时间数: {}'.format())
