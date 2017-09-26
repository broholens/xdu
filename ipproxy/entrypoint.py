"""
collect and validate ip
created at 2017-9-26 by broholens
"""

from ipproxy.collector import Collector
from ipproxy.validator import Validator
from ipproxy.settings import DB


class IpProxy:

    def __init__(self):
        self.collector = Collector()
        self.validator = Validator()
        self.db = DB

    def collect(self):
        self.collector.collect()

    def validate(self, proxy_list, key='good'):
        self.validator.validate(proxy_list, key)

    def get_db_proxies(self, collection='collector'):
        for proxy in self.db[collection].find({}, {'proxy': 1, '_id': 0}):
            yield proxy.get('proxy')


if __name__ == '__main__':
    ip = IpProxy()
    proxies = ip.get_db_proxies()
    ip.validate(proxies, 'available')
