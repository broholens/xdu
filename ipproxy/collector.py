import time
import random
import queue
import grequests

from ipproxy.utils import (
    Parser, request, logger, cut_queue, hour_delta, day_delta,
    exception_handler as eh
)
from ipproxy.settings import (
    RE_IP, RE_IP_2, DATA5U,
    PROXY_SITES, COLLECTION, PAGES, Q, ZDAYE_START_PAGE_ID,
)


class Collector:

    def __init__(self):
        self.logger = logger
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

        urls = list()

        # for api
        # urls.extend(
        #     [(api, self.parse_regex) for api in PROXY_SITES]
        # )

        # for data5u
        # urls.extend(
        #     [(f'http://www.data5u.com/dayip-{i}-10.html', self.parse_data5u)
        #      for i in range(1, sum((1, PAGES)))]
        # )

        # for ip3366
        # TODO: network firewall  (head/title -> network firewall)
        # urls.extend(
        #     [(f'http://www.ip3366.net/free/?stype={j}/page={i}', self.parse_regex_2)
        #      for i in range(1, sum((1, PAGES)))
        #      for j in range(1, 5)]
        # )

        # for httpdaili
        # urls.append(('http://www.httpdaili.com/mfdl/', self.parse_regex_2))

        # for mayi
        # now = day_delta()
        # urls.extend(
        #     [(f'http://www.mayidaili.com/share/view/{i}/', self.parse_regex)
        #      for i in range(now, now - PAGES, -1)]
        # )

        # for kuaidaili
        # urls.extend(
        #     [(f'http://www.kuaidaili.com/free/inha/{i}', self.parse_kuai)
        #      for i in range(1, sum((1, PAGES)))] +
        #     [(f'http://www.kuaidaili.com/free/intr/{i}', self.parse_kuai)
        #      for i in range(1, sum((1, PAGES)))]
        # )

        # for zdaye
        # now = hour_delta() + ZDAYE_START_PAGE_ID
        # urls.extend(
        #     [(f'http://ip.zdaye.com/dayProxy/ip/{i}.html', self.parse_regex)
        #      for i in range(now, now - PAGES, -1)]
        # )

        # for ip181
        # urls.extend(
        #     [(f'http://www.ip181.com/daili/{i}.html', self.parse_regex_2)
        #      for i in range(1, sum((1, PAGES)))]
        # )
        #
        # # for xici
        # urls.extend(
        #     [(f'http://www.xicidaili.com/nn/{i}', self.parse_xici)
        #      for i in range(1, sum((1, PAGES)))]
        # )
        #
        # # for mimi
        # urls.extend(
        #     [(f'http://www.mimiip.com/gngao/{i}', self.parse_regex_2)
        #      for i in range(1, sum((1, PAGES)))] +
        #     [(f'http://www.mimiip.com/gnpu/{i}', self.parse_regex_2)
        #      for i in range(1, sum((1, PAGES)))]
        # )

        random.shuffle(urls)
        for url in urls:
            self.q.put(url)

    def parse_regex(self, response):
        self.storage(RE_IP.findall(response.text), response.url)

    def parse_regex_2(self, response):
        ips = list()
        for ip in RE_IP_2.findall(response.text):
            host, port = ip.split('<', 1)
            port = port.split('>')[-1]
            ips.append(f'{host}:{port}')
        self.storage(ips, response.url)

    def parse_data5u(self, response):
        for url in DATA5U.findall(response.text):
            self.q.put((url, self.parse_regex))

    def parse_kuai(self, response):
        parser = Parser(response,
                        '//*[@id="list"]/table/tbody/tr',
                        './td[@data-title="IP"]/text()',
                        './td[@data-title="PORT"]/text()'
                        )
        ips = parser.parse(self.q, self.parse_kuai)
        self.storage(ips, response.url)

    def parse_xici(self, response):
        parser = Parser(response,
                        '//table[@id="ip_list"]/tr[position()>2]',
                        './td[2]/text()',
                        './td[3]/text()'
                        )
        ips = parser.parse(self.q, self.parse_xici)
        self.storage(ips, response.url)

    def collect(self, concurrent_num=3):
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
            # time.sleep(30)
