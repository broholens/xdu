"""
validate whether ip is useful or not

created at 2017-9-25 by broholens
"""

from gevent import monkey; monkey.patch_all()
import re
import random

import requests
import gevent
from pymongo import MongoClient

from ipproxy import settings

HOST = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}')


class Validator:

    def __init__(self):
        # result of httpbin is different from ip181
        self.db = MongoClient(settings.MONGO).ipproxy

    def validate(self, proxy_list):
        tasks = [
            gevent.spawn(ip_validator, proxy) for proxy in proxy_list
        ]
        gevent.joinall(tasks)
        for task in tasks:
            if task.value:
                self.storage(task.value)

        tasks = [
            gevent.spawn(website_validator, proxy) for proxy in proxy_list
        ]
        gevent.joinall(tasks)
        for task in tasks:
            if task.value:
                self.storage(task.value, 'available')

    def storage(self, proxy, key='good'):
        self.db.proxies.update_one(
            {'proxy': proxy},
            {
                '$set': {'proxy': proxy},
                '$addToSet': {'type': key},
                '$inc': {key+'_times': 1, 'detect_times': 1},
                '$currentDate': {'lastModified': True}
            },
            upsert=True
        )


def request(url, proxy, timeout=5):
    """
    catch exception
    :return: response if ok else None
    """
    try:
        return requests.get(url, proxies=proxy, timeout=timeout)
    except:
        return None


def ip_validator(proxy):
    """
    validate ip usable by some websites that return ip
    :param proxy: something like {'http': 'http://162.243.107.120:3128'}
    :return: proxy if usable else None
    """
    url = random.choice(settings.TEST_SITES)
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
    url = random.choice(settings.WEBSITES)
    resp = request(url, proxy)
    if resp and resp.status_code == 200:
        return proxy
