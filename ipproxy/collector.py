import time
import random
import queue
import grequests

from ipproxy.utils import (
    Parser, request, logger, cut_queue, hour_delta, day_delta,
    exception_handler as eh
)
from ipproxy.settings import (
    RE_IP, DATA5U, XS_START, XS_END,
    PROXY_SITES, COLLECTION, PAGES, Q, ZDAYE_START_PAGE_ID,
)


class Collector:

    def __init__(self):
        self.logger = logger
        self.q = queue.Queue()
        self.proxy_q = queue.Queue()
        self.put_to_queue()

    def storage(self, ips):
        if not ips:
            return
        for ip in ips:
            proxy = {'http': f'http://{ip}', 'https': f'https://{ip}'}
            Q.put(proxy)
            # self.proxy_q.put(proxy)
            COLLECTION.update_one(
                {'proxy': proxy},
                {'$set': {'proxy': proxy}},
                upsert=True
            )

    def put_to_queue(self):

        urls = list()

        # for api
        urls.extend(
            [(api, self.parse_regex) for api in PROXY_SITES]
        )

        # for data5u
        # urls.extend(
        #     [(f'http://www.data5u.com/dayip-{i}-10.html', self.parse_data5u)
        #      for i in range(1, sum((1, 290)))]
        # )

        # for ip3366
        # TODO: network firewall  (head/title -> network firewall)
        # urls.extend(
        #     [(f'http://www.ip3366.net/free/?stype={j}/page={i}', self.parse_regex_2)
        #      for i in range(1, sum((1, PAGES)))
        #      for j in range(1, 5)]
        # )

        # for mayi
        # now = day_delta() - 18
        # urls.extend(
        #     [(f'http://www.mayidaili.com/share/view/{i}/', self.parse_regex)
        #      # for i in range(now, now - PAGES, -1)]
        #      for i in range(now, 1, -1)]
        # )

        # for kuaidaili todo: 1001-1890
        # urls.extend(
        #     [(f'http://www.kuaidaili.com/free/inha/{i}', self.parse_regex)
        #      for i in range(1, sum((1, 1000)))]  # +
        #     # [(f'http://www.kuaidaili.com/free/intr/{i}', self.parse_kuai)
        #     #  for i in range(1, sum((1, PAGES)))]
        # )

        # for zdaye+
        # now = hour_delta() + ZDAYE_START_PAGE_ID
        # urls.extend(
        #     [(f'http://ip.zdaye.com/dayProxy/ip/{i}.html', self.parse_regex)
        #      for i in range(now, now - 795, -1)]
        # )

        # for ip181+
        # urls.extend(
        #     [(f'http://www.ip181.com/daili/{i}.html', self.parse_regex)
        #      for i in range(1, sum((1, 690)))]
        # )
        #
        # # for xici
        # urls.extend(
        #     [(f'http://www.xicidaili.com/nn/{i}', self.parse_regex)
        #      for i in range(1, sum((1, 1000)))]
        # )
        #
        # # for mimi
        # urls.extend(
        #     [(f'http://www.mimiip.com/gngao/{i}', self.parse_regex_2)
        #      for i in range(1, sum((1, 680)))] +
        #     [(f'http://www.mimiip.com/gnpu/{i}', self.parse_regex_2)
        #      for i in range(1, sum((1, 100)))]
        # )

        # for xiaoshu+
        now = day_delta(XS_START, XS_END) * 2 + 27
        urls.extend(
            [(f'http://www.xsdaili.com/dayProxy/ip/{i}.html', self.parse_regex)
             for i in range(now, 1, -1)]  # not contains 1
        )

        # for goubanjia
        # TODO: 504
        # 'http://www.goubanjia.com/free/'

        # for xiaoma
        # TODO: new regex
        # 'http://yun-daili.com/free.asp'

        # for pachong
        # TODO: not update
        # 'http://www.pcdaili.com/index.php'

        random.shuffle(urls)
        for url in urls:
            self.q.put(url)

    def parse_regex(self, response):
        ips = RE_IP.findall(response.text)
        if '</td>' not in ips[0] and ':' in ips[0]:
            self.storage(ips)
            return

        ips = (f'{ip.split("<")[0]}:{ip.split(">")[-1]}' for ip in ips)
        self.storage(ips)

    def parse_data5u(self, response):
        matches = DATA5U.findall(response.text)
        if not matches:
            self.logger.error('%s matches nothing', response.url)
            self.q.put((response.url, self.parse_data5u))
            return
        for url in matches:
            self.q.put((url, self.parse_regex))

    # def parse_kuai(self, response):
    #     parser = Parser(response,
    #                     '//*[@id="list"]/table/tbody/tr',
    #                     './td[@data-title="IP"]/text()',
    #                     './td[@data-title="PORT"]/text()'
    #                     )
    #     ips = parser.parse(self.q, self.parse_kuai)
    #     self.storage(ips, response.url)

    # def parse_xici(self, response):
    #     parser = Parser(response,
    #                     '//table[@id="ip_list"]/tr[position()>2]',
    #                     './td[2]/text()',
    #                     './td[3]/text()'
    #                     )

    #     ips = parser.parse(self.q, self.parse_xici)
    #     self.storage(ips, response.url)

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
            # time.sleep(3)
