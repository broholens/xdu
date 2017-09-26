"""
utils
created at 2017-9-26 by broholens
"""

from gevent import monkey; monkey.patch_all()
import gevent
import requests
import arrow
from ipproxy.settings import (START, END, TIMEOUT)


def request(url, proxy=None, timeout=TIMEOUT):
    """
    catch exception
    :return: response if ok else None
    """
    try:
        return requests.get(url, proxies=proxy, timeout=timeout)
    except:
        return None


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


def exe_tasks(func, task_list):
    """gevent exe"""
    tasks = [gevent.spawn(func, task) for task in task_list]
    gevent.joinall(tasks)
    return [task.value for task in tasks if task.value]