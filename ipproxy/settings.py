
# website validators

WEBSITES = [
        'http://www.firefox.com.cn/',
        'http://www.asus.com.cn/',
        'http://www.sina.com.cn/',
        'http://www.qq.com/',
        'http://news.163.com/',
        'http://yule.sohu.com/',
        'http://ent.163.com/',
        'http://news.qq.com/',
        'http://www.toutiao.com/',
        'http://www.csdn.net/',
        'http://www.7c.com/',
        'http://www.9ku.com/',
        'http://www.9553.com/',
        'http://www.eeyy.com/',
        'http://www.cr173.com/',
        'http://www.ddooo.com/',
        'http://iphone.tgbus.com/',
        'http://soft.hao123.com/',
        'http://www.xitongzhijia.net/',
        'http://www.xdowns.com/',
        'http://www.xinhuanet.com/',
        'http://www.cctv.com/',
        'http://www.tom.com/',
        'http://www.tianwang.com/',
        'http://www.365tq.com/',
        'http://nbtg3.00tera.com/',
        'http://bj.58.com/',
        'http://www.tuniu.com/',
        'http://www.baike.com/',
        'http://weego-hotel.oss-cn-beijing.aliyuncs.com/',
        'http://weegotr.com/',
        'http://fanyi.youdao.com/',
        'http://www.shenma.com/',
        'http://sh.ganji.com/',
        'https://note.youdao.com/',
        'https://www.qunar.com/',
        'https://www.baidu.com/',
        'https://cn.bing.com/',
        'https://www.douban.com/',
        'https://www.jd.com/',
        'https://www.1688.com/',
        'https://www.tmall.com/',
        'https://www.alibaba.com/',
        'https://www.alitrip.com/',
        'https://news.sohu.com/',
        'https://www.tencent.com/zh-cn/index.html',
        'https://top.51.la/',
        'https://www.hao123.com/',
        'https://www.360.cn/',
        'https://github.com/',
        # 'https://www.hotels.cn/',
        # 'https://www.tripadvisor.cn/',
        'https://www.cnblogs.com/',
        'https://www.sogou.com/',
        'https://www.114la.com/'
    ]


TESTSITES = {
    'http': [
        'http://ip.cn/',
        'http://httpbin.org/ip',
        'http://whatismyip.org/',
        'http://2017.ip138.com/ic.asp',
        'http://www.iprivacytools.com/proxy-checker-anonymity-test/',
        'http://www.proxylists.net/proxyjudge.php',
        # 'http://www.cnproxy.com/ipwhois.php',
        'http://ip.chinaz.com/getip.aspx',
        'http://ip.chacuo.net/',
        'http://ipaddress.my/',
        'http://www.myipaddress.com/',
        'http://addgadgets.com/ipaddress/',
        'http://www.ipaddressden.com/',
        'http://www.ipaddresslocation.org/',
        'http://ipchicken.com/',
        'http://www.ipaddressapi.com/',
        'http://checkip.dyndns.com/',
        'http://www.btcha.com/ip.html',
        'http://hidingipaddress.com/'
    ],
    'https': [
        'https://httpbin.org/ip',
        'https://www.whatismyip.com/',
        'https://whatismyipaddress.com/',
        'https://www.ip-address.org/',
        'https://www.iplocation.net/',
        'https://www.ip2location.com/',
        'https://www.ipaddress.com/',
        'https://www.findip-address.com/',
        'https://www.myip.ms/',
        'https://www.1and1.com/ip-address',
        'https://ipaddress.pro/',
        'https://www.whoisthisip.com/',
        'https://www.find-ip.net/',
        'https://ipinfo.io/',
        'https://ipfind.co/',
        'https://www.find-ip.net/'
    ]
}

# proxies to be collected  parsed by regex
PROXY_SITES = [
    'https://www.rmccurdy.com/scripts/proxy/good.txt',
    'http://www.proxylists.net/http_highanon.txt',
    'http://ab57.ru/downloads/proxyold.txt',
    'http://www.66ip.cn/nmtq.php?getnum=500&anonymoustype=4&proxytype=2&api=66ip'
]

# mongouri
MONGO = 'mongodb://localhost:27017'


from datetime import datetime
START = datetime(2017, 9, 26, 9)
END = datetime.now()

import re
HOST = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
PORT = re.compile('\d{1,5}')
IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}')
ZDAYE_PAGE_ID = re.compile('/dayProxy/ip/\d+.html')
ZDAYE_START_PAGE_ID = 6392

from pymongo import MongoClient
COLLECTION = MongoClient(MONGO).ip.ipproxy

from multiprocessing import Queue
Q = Queue()

TIMEOUT = 5

PAGES = 2
