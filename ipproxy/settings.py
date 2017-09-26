
# website validators

WEBSITES = [
    'https://www.baidu.com/',
    'https://cn.bing.com/',
    'http://www.firefox.com.cn/',
    'http://www.asus.com.cn/'
    'https://www.douban.com/',
    'https://www.jd.com/',
    'https://www.1688.com/',
    'http://www.sina.com.cn/',
    'http://www.qq.com/'
]

TEST_SITES = [
    'http://httpbin.org/ip',
    'http://2017.ip138.com/ic.asp',
    'http://www.iprivacytools.com/proxy-checker-anonymity-test/',
    'http://www.proxylists.net/proxyjudge.php',
    'http://www.cnproxy.com/ipwhois.php',
    'http://ip.chinaz.com/getip.aspx'
]

# proxies to be collected
PROXY_SITES = [
    'https://www.rmccurdy.com/scripts/proxy/good.txt',
    'http://www.proxylists.net/http_highanon.txt',
    'http://ab57.ru/downloads/proxyold.txt'
]

# mongouri
MONGO = 'mongodb://localhost:27017'


from datetime import datetime
START = datetime(2017, 9, 26, 9)
END = datetime.now()

import re
HOST = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}')
ZDAYE_PAGE_ID = re.compile('/dayProxy/ip/\d+.html')
ZDAYE_START_PAGE_ID = 6392

from pymongo import MongoClient
DB = MongoClient(MONGO).ipproxy

TIMEOUT = 60
