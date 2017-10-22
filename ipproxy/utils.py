"""
utils
created at 2017-9-26 by broholens
"""

import logging
import grequests
import arrow
from lxml import etree
from fake_useragent import UserAgent
from ipproxy.settings import (START, END, TIMEOUT, HOST, PORT)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s %(levelname)s %(message)s'
)

logger = logging.getLogger(__name__)


def request(url, proxy=None, timeout=TIMEOUT, is_map=False, retry=False):
    """
    catch exception
    :return: response if ok else None
    """
    header = {'User-Agent': UserAgent().random}
    # try:
    req = grequests.get(url, proxies=proxy, headers=header, timeout=timeout)
    logger.info('fetching %s %s', url, proxy)
    if is_map is False:
        req.send()
        return req.response
    return req
    # except:
    #     logger.error('failed to request %s', url)
    #     if retry is False:
    #         return
    #     request(url, proxy=proxy, timeout=timeout, is_map=is_map, retry=retry)


def m_request(urls):
    rs = (request(url, is_map=True) for url in urls)
    return [resp for resp in grequests.map(rs) if resp]


def cut_queue(q, length):
    if q.qsize() > length:
        return [q.get() for _ in range(length)]
    return [q.get() for _ in range(q.qsize())]


def cut_list(seq, length):
    num = length if len(seq) > length else len(seq)
    return [seq.pop() for _ in range(num)]


class Parser:

    def __init__(self, response, ips_xp, host_xp, port_xp):
        self.response = response
        self.host_xp = host_xp
        self.port_xp = port_xp
        self.xp = ips_xp
        self.tree = self.to_tree()

    def validate_ip(self, host, port):
        return (HOST.findall(host) and HOST.findall(host)[0],
                PORT.findall(port) and PORT.findall(port)[0])

    def to_tree(self):
        return etree.HTML(self.response.text)

    def extract(self, tree, xp, first=True):
        try:
            values = tree.xpath(xp)
        except:
            logger.error('cannot parse xpath %s %s', xp, self.response.url)
            return
        if not values:
            return
        if first is True:
            return values[0]
        return values

    def parse(self, q, method):
        ips = self.extract(self.tree, self.xp, first=False)
        if not ips:
            logger.error('failed to fetch ip of %s', self.response.url)
            q.put((self.response.url, method))
            return
        for ip in ips:
            host = self.extract(ip, self.host_xp)
            port = self.extract(ip, self.port_xp)
            host, port = self.validate_ip(host, port)
            if not (host and port):
                logger.error('wrong ip %s:%s %s', host, port, self.response.url)
                continue
            yield f'{host}:{port}'


def exception_handler(request, exception):
    pass


def hour_delta(start=START, end=END, tz='local'):
    """
    calculate hours from end to start
    :param start: datetime
    :param end: datetime
    :param tz: https://arrow.readthedocs.io/en/latest/#tz-expr
    :return: diff days
    """
    start = arrow.get(start, tz)
    now = arrow.get(end, tz)
    return (now - start).days * 24 + now.hour - start.hour


# def exe_tasks(func, task_list):
#     """gevent exe"""
#     tasks = [gevent.spawn(func, task) for task in task_list]
#     gevent.joinall(tasks)
#     return [task.value for task in tasks if task.value]
