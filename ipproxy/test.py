import queue
import json

import requests
import grequests

from ipproxy.collector import Collector
from ipproxy.utils import request, cut_queue
from ipproxy.settings import RE_HOST


api_get_url = 'http://0.0.0.0:8080/get'
api_detect_url = 'http://0.0.0.0:8080/increase_detect_times'
api_alive_url = 'http://0.0.0.0:8080/increase_alive_times'

urls = list()


# for data5u
# urls.extend(
#     [f'http://www.data5u.com/dayip-{i}-10.html' for i in range(1, sum((1, 290)))]
# )

# for ip3366
# TODO: network firewall  (head/title -> network firewall)
urls.extend(
    [f'http://www.ip3366.net/free/?stype={b}/page={c}'
     for c in range(1, sum((1, 7)))
     for b in range(1, 5)]
)


# for xici
urls.extend(
    [f'http://www.xicidaili.com/nn/{d}'
     for d in range(1, sum((101, 1000)))]
)

# for mimi
urls.extend(
    [f'http://www.mimiip.com/gngao/{e}'
     for e in range(1, sum((1, 680)))] +
    [f'http://www.mimiip.com/gnpu/{f}'
     for f in range(1, sum((1, 100)))]
)


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
                if not resp or len(RE_HOST.findall(resp.text)) < 5:
                    self.logger.error('recycle: %s', url)
                    self.q.put(url)
                    requests.post(api_detect_url, data=json.dumps(proxy))
                    continue
                self.logger.info('fetched: %s', url)
                self.logger.info('%s', RE_HOST.findall(resp.text))
                requests.post(api_alive_url, data=json.dumps(proxy))
                self.parse_regex(resp)


if __name__ == '__main__':
    my_collector = MyCollector(urls)
    my_collector.collect()
    # c = Collector()
    # c.collect()

