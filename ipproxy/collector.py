"""
ip collector
created at 2017-9-26 by broholens
"""

from itertools import chain
from ipproxy.utils import request, hour_delta, exe_tasks
from ipproxy.settings import (
    IP, ZDAYE_PAGE_ID, ZDAYE_START_PAGE_ID as START_ID, PROXY_SITES, DB
)


class Collector:
    def __init__(self):
        self.db = DB

    def collect(self):
        urls = set(chain(PROXY_SITES, zdaye_all()))
        for resp in exe_tasks(request, urls):
            for ip in IP.finditer(resp.text):
                self.storage({'http': f'http://{ip.group(0)}'})

    def storage(self, proxy):
        self.db.collector.update_one(
            {'proxy': proxy},
            {
                '$set': {'proxy': proxy},
                '$inc': {'detect_times': 1},
                '$currentDate': {'lastModified': True}
            },
            upsert=True
        )


def zdaye(count=24):
    """
    get ips from zdaye.com
    :param count: the last 24 pages, daily
    :return: list of urls
    """
    max_id = hour_delta() + START_ID
    return [
        f'http://ip.zdaye.com/dayProxy/ip/{page_id}.html'
        for page_id in range(max_id - count, max_id + 1)
    ]


def zdaye_all():
    """
    get ips of 2017.1-2017.9
    """
    page_urls = set()
    host = 'http://ip.zdaye.com'
    month_urls = [host+f'/dayProxy/2017/{i}/1.html' for i in range(1, 9)] + \
                 [host+f'/dayProxy/2017/{i}/2.html' for i in range(1, 9)]
    month_urls += [host+f'/dayProxy/2017/9/{i}.html' for i in range(1, 13)]
    for resp in exe_tasks(request, month_urls):
        for page_id in ZDAYE_PAGE_ID.finditer(resp.text):
            page_urls.add(host+page_id.group(0))
    return page_urls
