
from datetime import datetime
from random import choice
from multiprocessing import Process, JoinableQueue, Queue

import grequests
from bson.objectid import ObjectId

from ipproxy.utils import request, logger, cut_queue, exception_handler as eh
from ipproxy.settings import (
    COLLECTION, TESTSITES, WEBSITES, TIMEOUT, RE_HOST, HIGH_ANONYMOUS
)


class Validator:

    def __init__(self):
        self.logger = logger
        self.count_website_ok = 0
        self.count_testsite_ok = 0
        self.proxy_validated_q = JoinableQueue()
        self.real_time_q = Queue()
        self.proxy_source_q = Queue()
        self.my_ip = self.get_my_ip()

    def get_my_ip(self):
        resp = request('http://httpbin.org/ip')
        if not resp:
            raise ValueError('cannot get my ip!')
        self.logger.info('my ip: %s', resp.json().get('origin'))
        return resp.json().get('origin')

    def clear_up_db_proxies(self):
        COLLECTION.delete_many({'type': ['normal']})
        COLLECTION.delete_many({'alive_times': None})
        COLLECTION.delete_many({'score': {'$lt': 0.5}})

    def get_db_proxies(self):
        for proxy in COLLECTION.find():
            self.proxy_source_q.put(proxy.get('proxy'))

    def get_proxies(self, proxies_seq):
        for proxy in proxies_seq:
            self.proxy_source_q.put(proxy)
        # pass

    # availability of ip is too low, use ipsite you must *2, so filter them
    def website_validate(self, q, concurrent_num=50):
        while not q.empty():
            self.logger.info('source qsize: %s', q.qsize())
            proxies = cut_queue(q, concurrent_num)
            self._web_validator(proxies)
        self.proxy_validated_q.join()
        self.clear_up_db_proxies()

    def _web_validator(self, proxies):
        rs = (request(choice(WEBSITES), proxy=proxy, is_map=True)
              for proxy in proxies)

        resps = grequests.map(rs, gtimeout=TIMEOUT, exception_handler=eh)
        for resp, proxy in zip(resps, proxies):
            COLLECTION.update_one(
                {'proxy': proxy},
                {
                    '$set': {'proxy': proxy},
                    '$inc': {'detect_times': 1},
                },
                upsert=True
            )
            if not resp or resp.status_code != 200:
                continue

            self.proxy_validated_q.put(proxy)

            self.count_website_ok += 1
            self.logger.info('websites available: %s %s %s',
                             self.count_website_ok,
                             proxy,
                             resp.url)

            COLLECTION.update_one(
                {'proxy': proxy},
                {
                    '$addToSet': {'type': 'normal'},
                    '$inc': {'alive_times': 1}
                }
            )

    def test_validate(self):
        while True:
            self._test_validator(self.proxy_validated_q.get())
            self.proxy_validated_q.task_done()

    def _test_validator(self, proxy):
        COLLECTION.update_one(
            {'proxy': proxy},
            {'$inc': {'detect_times': 1}}
        )
        detect_times_label = 0
        http, https = {'http': proxy.get('http')}, {'https': proxy.get('https')}
        reqs = (
            request(choice(TESTSITES.get('http')), proxy=http, is_map=True),
            request(choice(TESTSITES.get('https')), proxy=https, is_map=True)
        )
        resps = grequests.map(reqs, gtimeout=10, exception_handler=eh)
        for index, resp in enumerate(resps):
            if not resp:
                continue

            matches = RE_HOST.findall(resp.text)
            if not matches or self.my_ip in matches:
                continue

            p = (https, 'https') if index > 0 else (http, 'http')
            r = request(p[0], timeout=10)
            if r:
                continue

            self.real_time_q.put(p)

            self.logger.info('%s, %s', matches, proxy)

            detect_times_label += 1

            if detect_times_label == 2:
                COLLECTION.update_one(
                    {'proxy': proxy},
                    {'$inc': {'detect_times': 1}}
                )

            self.count_testsite_ok += 1

            cursor = COLLECTION.find_one({'proxy': proxy})
            this_id = cursor.get('_id')
            alive_times = cursor.get('alive_times') + 1
            detect_times = cursor.get('detect_times')
            # [0, 1]
            score = alive_times * 2 / (alive_times + detect_times)
            self.logger.info('high anonymity: %s score: %s %s %s',
                             self.count_testsite_ok,
                             score,
                             p[0],
                             resp.url)
            COLLECTION.update_one(
                {'_id': ObjectId(this_id)},
                {
                    '$set': {'score': score},
                    '$push': {'alive_time_base': datetime.now()},
                    '$addToSet': {
                        'type': 'high',
                        'protocol': p[1]
                    },
                    '$inc': {'alive_times': 1}
                }
            )

    def real_time(self):
        while True:
            proxy, protocol = self.real_time_q.get()

            # if not proxy:
            #     time.sleep(60*2)
            self.logger.info('real time testing: %s', proxy)
            # TODO: websites http https
            resp = request('https://www.baidu.com/', proxy=proxy, timeout=5)

            if not resp:
                self.logger.info('dead: %s', proxy)
                continue

            self.logger.info('still alive: %s', proxy)
            self.real_time_q.put(proxy)
            HIGH_ANONYMOUS.update_one(
                {'proxy': proxy},
                {
                    '$set': {'proxy': proxy, 'protocol': protocol},
                    '$inc': {'alive_times': 1},
                    '$push': {'alive_time_base': datetime.now()}
                },
                upsert=True
            )

    def validate(self, db_proxies=True, proxies_seq=None):
        if db_proxies is True:
            self.get_db_proxies()
        elif proxies_seq:
            self.get_proxies(proxies_seq)
        else:
            self.logger.error('source of proxies is empty!')
            raise ValueError('source of proxies is empty!')
        p1 = Process(target=self.website_validate, args=(self.proxy_source_q,))
        p2 = Process(target=self.test_validate)
        p2.daemon = True
        p1.start()
        p2.start()
        p1.join()
        # self.logger.info('high: %s, normal: %s',
        #                  self.count_testsite_ok,
        #                  self.count_website_ok)
