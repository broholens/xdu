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
        self.pages = 5
        self.source_urls = []
        self.zdaye_max = hour_delta() + START_ID
        self.source_list = [
            # zdaye
            ('http://ip.zdaye.com/dayProxy/ip/{}.html',
             self.zdaye_max-self.pages, self.zdaye_max+1),
            # proxy-list not work ConnectTimeout
            # ('http://proxy-list.org/english/search.php?ssl=no&p={}',
            #  1, self.pages+1)
        ]
        self.generate_source_urls()

    def collect(self):
        urls = chain(PROXY_SITES, self.source_urls)
        # urls = zdaye_all()
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

    def generate_source_urls(self):
        """get pages url whose ip likes 192.168.1.1:8080"""
        for source in self.source_list:
            self.source_urls.extend([
                source[0].format(page_id)
                for page_id in range(source[1], source[2])
            ])


def zdaye_all():
    """
    get ips of 2017.1-2017.8
    """
    page_urls = set()
    host = 'http://ip.zdaye.com'
    month_urls = [
        host+f'/dayProxy/2017/{i}/{j}.html'
        for i in range(1, 9)
        for j in [1, 2]
    ]
    for resp in exe_tasks(request, month_urls):
        for page_id in ZDAYE_PAGE_ID.finditer(resp.text):
            page_urls.add(host+page_id.group(0))
    # DB.zdaye.insert_many(map(lambda i: {'url': i}, page_urls))
    return page_urls
