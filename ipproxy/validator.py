"""
validate whether ip is useful or not

created at 2017-9-25 by broholens
"""

import random
from ipproxy.settings import (DB, TEST_SITES, HOST, WEBSITES)
from ipproxy.utils import request, exe_tasks, logger


class Validator:

    def __init__(self):
        # result of httpbin is different from ip181
        self.db = DB
        self.logger = logger
        self.validator = {
            'good': self.ip_validator,
            'available': self.website_validator
        }

    def validate(self, proxy_list, key='good'):
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

    def ip_validator(self, proxy):
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
        self.logger.info('ip validator: available proxy - %s', proxy)
        return proxy
        # distinguish anonymous level
        # matches = HOST.findall(resp.text)
        # if proxy.get('http').split(':')[1][2:] in matches:
        #     self.logger.info('ip validator: %s', proxy)
        #     return proxy
        # self.logger.error('? %s', resp.text)
        # self.logger.error('ip validator: useless ip %s', proxy)

    def website_validator(self, proxy):
        """
        likes ip_validator except uses website like baidu
        """
        url = random.choice(WEBSITES)
        resp = request(url, proxy)
        if not resp:
            return None
        if resp.status_code == 200:
            self.logger.info('website validator: available proxy - %s', proxy)
            return proxy
        self.logger.error('website validator: useless proxy %s', proxy)
