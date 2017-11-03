import time
from random import choice
from multiprocessing import Queue, JoinableQueue, Process

import grequests
from pymongo import MongoClient
from selenium import webdriver
# from selenium.webdriver.common.proxy import *  # for firefox

from ipproxy.utils import request, cut_queue

col = MongoClient().ip.ipproxy

db_proxies_q = Queue()

for proxy in col.find({'protocol': {'$in': ['https']}}, {'proxy': 1, '_id': 0}):
    db_proxies_q.put(proxy)

good_proxies_q = JoinableQueue()


def baidu():
    while not db_proxies_q.empty():
        proxies = cut_queue(db_proxies_q, 10)
        rs = (request('https://www.baidu.com', proxy=proxy, is_map=True)
              for proxy in proxies)
        resps = grequests.map(rs, gtimeout=10)
        for proxy, resp in zip(proxies, resps):
            if not resp:
                continue
            print(proxy)
            good_proxies_q.put(proxy.get('https').lstrip('https://'))
    good_proxies_q.join()

# def add_proxy(proxy):
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument(f'--proxy-server={proxy}')
#     return webdriver.Chrome(chrome_options=chrome_options)


ok_num = 0


def work():
    while True:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={good_proxies_q.get()}')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver = webdriver.Chrome()
        try:
            driver.set_page_load_timeout(60)

            driver.get('https://www.wjx.cn/m/17745242.aspx')

            # 1-11
            for a in range(1, 12):
                choice(driver.find_elements_by_xpath(f'//*[@id="div{a}"]//a')).click()

            # 12
            for b in range(1, 20):
                choice(driver.find_elements_by_xpath(f'//*[@id="drv12_{b}"]//a')).click()

            # 13
            for c in range(1, 20):
                choice(driver.find_elements_by_xpath(f'//*[@id="drv13_{c}"]//a')).click()

            # 15-38
            for d in range(15, 39):
                choice(driver.find_elements_by_xpath(f'//*[@id="div{d}"]//a')).click()

            # submit
            driver.find_element_by_id('ctlNext').click()

            global ok_num
            ok_num += 1
            print(ok_num)

            time.sleep(2)
        except:
            continue
        finally:
            good_proxies_q.task_done()
            driver.close()


if __name__ == '__main__':
    # work()
    process_num = 3

    p1 = Process(target=baidu)
    p1.start()

    workers = []
    for _ in range(process_num):
        p = Process(target=work)
        p.daemon = True
        workers.append(p)
    for worker in workers:
        worker.start()

    p1.join()

    print(ok_num * process_num)
