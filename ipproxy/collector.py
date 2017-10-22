import time
import random
import queue
import grequests

from ipproxy.utils import (Parser,
                           request, logger, cut_queue, exception_handler as eh)
from ipproxy.settings import IP, PROXY_SITES, COLLECTION, PAGES, Q


class Collector:

    def __init__(self):
        self.logger = logger
        self.page_mimi = [1, PAGES]
        self.page_ip181 = [101, 596]
        self.page_xici = [1, 300]
        self.q = queue.Queue()
        self.put_to_queue()

    def _storage(self, proxy, response_url):
        # protocol = 'http' if proxy.get('http') else 'https'
        COLLECTION.update_one(
            {'proxy': proxy},
            {
                '$set': {'proxy': proxy},
                '$push': {'source': response_url},
                '$currentDate': {'lastModified': True}
            },
            upsert=True
        )

    def storage(self, ips, response_url):
        if not ips:
            return
        for ip in ips:
            proxy = {'http': f'http://{ip}', 'https': f'https://{ip}'}
            Q.put(proxy)
            self._storage(proxy, response_url)

    def put_to_queue(self):
        # urls = [(f'http://www.mimiip.com/gngao/{i}', self.parse_mimiip)
        #         for i in range(self.page_mimi[0], sum(self.page_mimi))] + \

        urls = [(f'http://www.ip181.com/daili/{i}.html', self.parse_ip181)
                for i in range(self.page_ip181[0], sum(self.page_ip181))] # + \
               # [(f'http://www.xicidaili.com/nn/{i}', self.parse_xici)
               #  for i in range(self.page_xici[0], sum(self.page_xici))]
               # [(url, self.parse_regex) for url in PROXY_SITES]

        random.shuffle(urls)
        for url in urls:
            self.q.put(url)

    def parse_regex(self, response):
        self.storage(IP.findall(response.text), response.url)

    def parse_mimiip(self, response):
        parser = Parser(response,
                        '//table[@class="list"]/tr[position()>1]',
                        './td[1]/text()',
                        './td[2]/text()'
                        )
        ips = parser.parse(self.q, self.parse_mimiip)
        self.storage(ips, response.url)

    def parse_ip181(self, response):
        parser = Parser(response,
                        '//table[contains(@class, "table-hover")]/tbody/tr[position()>2]',
                        './td[1]/text()',
                        './td[2]/text()'
                        )
        ips = parser.parse(self.q, self.parse_ip181)
        self.storage(ips, response.url)

    def parse_xici(self, response):
        parser = Parser(response,
                        '//table[@id="ip_list"]/tr[position()>2]',
                        './td[2]/text()',
                        './td[3]/text()'
                        )
        ips = parser.parse(self.q, self.parse_xici)
        self.storage(ips, response.url)

    def collect(self, concurrent_num=5):
        while not self.q.empty():
            elements = cut_queue(self.q, concurrent_num)
            reqs = (request(ele[0], is_map=True) for ele in elements)
            resps = grequests.map(reqs, gtimeout=10, exception_handler=eh)
            for resp, element in zip(resps, elements):
                if not resp:
                    self.q.put(element)
                    self.logger.error('recycle %s', element[0])
                    continue
                self.logger.info('fetched %s', resp.url)
                element[1](resp)
            time.sleep(30)

