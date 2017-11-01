
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
        # 'http://www.iprivacytools.com/proxy-checker-anonymity-test/',
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
        # 'http://www.btcha.com/ip.html',
        'http://hidingipaddress.com/'
    ],
    'https': [
        'https://httpbin.org/ip',
        # 'https://www.whatismyip.com/',
        # 'https://whatismyipaddress.com/',
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
        # 'https://ipinfo.io/',
        'https://ipfind.co/'
    ]
}

# proxies to be collected  parsed by regex
PROXY_SITES = [
    'https://www.rmccurdy.com/scripts/proxy/good.txt',
    'http://www.proxylists.net/http_highanon.txt',
    'http://ab57.ru/downloads/proxyold.txt',
    'http://www.66ip.cn/mo.php?tqsl=500',
    # 'http://www.89ip.cn/apijk/?&tqsl=500',
    'http://www.httpdaili.com/mfdl/',
    'http://daili.iphai.com/',
    'http://ip.baizhongsou.com/',
    'http://www.66ip.cn/nmtq.php?getnum=500&anonymoustype=4&proxytype=2&api=66ip'
]

# User-Agent
UA = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
    "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
    "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
    "Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
    "Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02",
    "Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00",
    "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
    "Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00",
    "Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
    "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
    "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
    "Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; tr-TR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; ko-KR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; fr-FR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; cs-CZ) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; ja-JP) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_8; zh-cn) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_8; ja-jp) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; ja-jp) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; zh-cn) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27"
]

# mongouri
MONGO = 'mongodb://localhost:27017'


from datetime import datetime, date
# for zdaye
ZDY_START = datetime(2017, 9, 19, 20)
ZDY_END = datetime.now()
# for mayi
MAYI_START = date(2015, 4, 27)
MAYI_END = date.today()
# for xiaoshudaili
XS_START = date(2017, 5, 23)
XS_END = date.today()

import re
RE_HOST = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
RE_PORT = re.compile('\d{1,5}')
RE_IP = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[^0-9]+\d{1,5}')
DATA5U = re.compile('http://www.data5u.com/dayip/\d+.html')
ZDAYE_START_PAGE_ID = 6235


from pymongo import MongoClient
DB = MongoClient(MONGO).ip
COLLECTION = DB.ipproxy
HIGH_ANONYMOUS = DB.high

from multiprocessing import Queue
# queue for collect_validate()
Q = Queue()

# request timeout
# concurrent count 50
TIMEOUT = 8

# count of pages to crawl
PAGES = 2
