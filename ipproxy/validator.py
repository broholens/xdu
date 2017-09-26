"""
validate whether ip is useful or not

created at 2017-9-25 by broholens
"""

import random
from ipproxy.settings import (DB, TEST_SITES, HOST, WEBSITES)
from ipproxy.utils import request, exe_tasks


class Validator:

    def __init__(self):
        # result of httpbin is different from ip181
        self.db = DB
        self.validator = {
            'good': ip_validator,
            'available': website_validator
        }

    def validate(self, proxy_list):
        self._validate(proxy_list)
        self._validate(proxy_list, 'available')

    def _validate(self, proxy_list, key='good'):
        for proxy in exe_tasks(self.validator.get(key), proxy_list):
            self.storage(proxy, key)

    def storage(self, proxy, key='good'):
        self.db.validator.update_one(
            {'proxy': proxy},
            {
                '$set': {'proxy': proxy},
                '$addToSet': {'type': key},
                '$inc': {key+'_times': 1, 'detect_times': 1},
                '$currentDate': {'lastModified': True}
            },
            upsert=True
        )


def ip_validator(proxy):
    """
    validate ip usable by some websites that return ip
    :param proxy: something like {'http': 'http://162.243.107.120:3128'}
    :return: proxy if usable else None
    """
    if proxy is None:
        return None
    url = random.choice(TEST_SITES)
    resp = request(url, proxy)
    if not resp:
        return None
    matches = HOST.search(resp.text)
    if matches and matches.group(0) in proxy.get('http'):
        return proxy


def website_validator(proxy):
    """
    likes ip_validator except uses website like baidu
    """
    url = random.choice(WEBSITES)
    resp = request(url, proxy)
    if resp and resp.status_code == 200:
        return proxy
