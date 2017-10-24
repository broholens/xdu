"""
collect and validate ip
created at 2017-9-26 by broholens
"""

import time
from multiprocessing import Process

from ipproxy.collector import Collector
from ipproxy.validator import Validator
from ipproxy.settings import Q


class IPProxy:

    @staticmethod
    def collect():
        Collector().collect()

    @staticmethod
    def validate():
        Validator().validate()

    @staticmethod
    def collect_validate():
        collector = Collector()
        validator = Validator()
        p1 = Process(target=collector.collect)
        p2 = Process(target=validator.website_validate, args=(Q,))
        p3 = Process(target=validator.test_validate)
        p4 = Process(target=validator.real_time)
        # p1.daemon bad urls
        p1.daemon, p3.daemon = True, True
        p1.start()
        # to ensure task queue is not empty
        time.sleep(10)
        p2.start()
        p3.start()
        p4.start()
        p2.join()


# def run_ip_proxy():
#     while True:
#         ip = IPProxy()
#         daily_p = Process(target=ip.collect_validate)
#         validate_p = Process(target=ip.validate)
#         daily_p.start()
#         validate_p.start()
#         daily_p.join()
#         validate_p.join()
if __name__ == '__main__':
    IPProxy.collect_validate()
