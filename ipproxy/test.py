import queue
import json

import requests
import grequests

from ipproxy.collector import Collector
from ipproxy.utils import request, cut_queue


api_get_url = 'http://0.0.0.0:8080/get'
api_detect_url = 'http://0.0.0.0:8080/increase_detect_times'
api_alive_url = 'http://0.0.0.0:8080/increase_alive_times'

urls = [f'http://www.xicidaili.com/nn/{i}' for i in range(1, sum((1, 20)))]


class MyCollector(Collector):

    def __init__(self, urls):
        self.urls = urls
        Collector.__init__(self)
        self.proxy_q = queue.Queue()

    def put_to_queue(self):
        for url in self.urls:
            self.q.put(url)

    def get_proxies(self):
        for proxy in requests.get(api_get_url).json():
            self.proxy_q.put(proxy)

    def collect(self, concurrent_num=10):
        while not self.q.empty():
            if self.proxy_q.qsize() < concurrent_num:
                self.get_proxies()
            proxies = cut_queue(self.proxy_q, concurrent_num)
            _urls = cut_queue(self.q, concurrent_num)
            reqs = (request(u, proxy=p, is_map=True)
                    for u, p in zip(_urls, proxies))
            resps = grequests.map(reqs, gtimeout=10)
            for url, resp, proxy in zip(_urls, resps, proxies):
                if not resp:
                    self.logger.error('recycle: %s', url)
                    self.q.put(url)
                    requests.post(api_detect_url, data=json.dumps(proxy))
                    continue
                self.logger.info('fetched: %s', url)
                self.logger.info('%s', resp.text)
                requests.post(api_alive_url, data=json.dumps(proxy))
                self.parse_regex_2(resp)


if __name__ == '__main__':
    my_collector = MyCollector(urls)
    my_collector.collect()

