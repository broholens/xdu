from time import time
from queue import Queue
from random import choice
from operator import itemgetter

from pymongo import MongoClient, GEOSPHERE
from bson.objectid import ObjectId
from bson.son import SON

from ipproxy.utils import *
from ipproxy.settings import UA


class Ziroom:

    headers = {
    'Host': 'www.ziroom.com',
    'Connection': 'keep-alive',
    # 'Cache-Control': 'max-age=0',
    'User-Agent': choice(UA),
    # 'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

    keys = [
        '637ea37a488d5ada69b9add6b51ade91',
        'e1c83a76830ca6be62c67835ac12ad5c',
        '1aff8f5ae130e3703d4ba89f46c31df8',
        '1f6d0d8ea68c21088beec7e0ca5e7b1e',
        'd962e50247065e81077eb144175d5adc',
        'c5c96d4b1a01d417d046703ae06d88bd',
        '1cc614cd037bd367fe86ffd0d1094540',
        'f37aa948833a47f6107650e440aee4ed',
        '3415a2784ab651a9ae0135623c84eff3',
        '5c52252dd22fdbb9c0f337488d78d3a8'
    ]

    start_urls_dict = {
        'beijing': 'http://www.ziroom.com/z/nl/z3.html',
        'shanghai': 'http://sh.ziroom.com/z/nl/z3.html',
        'shenzhen': 'http://sz.ziroom.com/z/nl/z3.html',
        'hangzhou': 'http://hz.ziroom.com/z/nl/z3.html',
        'nanjing': 'http://nj.ziroom.com/z/nl/z3.html'
    }

    # 通过模糊地址获取位置信息（location， formatted_address）
    location_url = 'http://restapi.amap.com/v3/geocode/geo?key={0}&address={1}&city={2}'
    # 通过location获取附近POI(数量)
    prosperous_url = 'http://restapi.amap.com/v3/place/around?key={}&location={}&radius=1000&types=050000|060100|060400|070000'
    # 起点终点距离，公交耗时（可多个起点）
    distance_url = 'http://restapi.amap.com/v3/distance?key={}&origins={}&destination={}'

    concurrent_num = 10

    gtimeout = 10

    def __init__(self, city='beijing'):
        self.city = city  # 查询城市
        self.start_url = self.start_urls_dict.get(city)
        self.request_q = Queue()  # 存放能找到房间信息的链接
        self.after_room_ids = set()
        self.db = MongoClient().ziroom
        if 'location_2dsphere' not in self.db.ziroom.index_information():
            self.db.ziroom.create_index([('location', GEOSPHERE)])

    def get_index_urls(self):
        # 库中的房间可能会过期，如果这次搜到的房间跟库中不同，则要把库中sell状态设为off
        self.before_room_ids = [i['room_id'] for i in self.db.ziroom.find()]

        # 将某区某镇的房子的第一页链接放进request_q
        resp = request(self.start_url, header=self.headers)
        if not resp:
            raise ValueError('response is empty!')
        tree = to_tree(resp.text)
        urls = tree.xpath('//dl[@class="clearfix zIndex6"]//span/a/@href')
        for url in urls:
            # >20 为某区全部房间， 房间数量有可能大于50页， 不能显示完全
            if len(url.split('/')[-1]) < 20:
                continue
            self.request_q.put(request('http:' + url, is_map=True))

    def get_room_url(self, response):
        page = response.url.strip('/')
        response = to_tree(response.text)
        self.parse_room(response)

        pages = response.xpath('//span[@class="pagenum"]/text()')
        pages = 1 if not pages else int(pages[0].strip('"').strip('/'))

        # 每次都看看到没到最大页, 没到就继续往request_q里添加
        if pages == 1:
            return
        elif page.endswith('html'):
            self.request_q.put(request(page+'?p=2', is_map=True))
        elif int(page.split('=')[-1]) < pages:
            url = '='.join((page.split('=')[0], str(int(page.split('=')[-1])+1)))
            self.request_q.put(request(url, is_map=True))

    def parse_room(self, response):
        for room in response.xpath('//*[@id="houseList"]/li[@class="clearfix"]'):
            item = {}
            room_url = room.xpath('.//a[@class="t1"]/@href')[0]
            item['room_url'] = 'http:' + room_url
            item['room_id'] = room_url.strip('/').split('/')[-1].strip('.html')
            address = room.xpath('.//a[@class="t1"]/text()')[0]
            item['address'] = address
            district_subway = room.xpath('.//h4/a/text()')[0]
            district, subway = district_subway.split(']')
            item['district'] = district.strip('[')
            # TODO: 通过地铁搜索不行，　可靠虑调用api获取地铁情况
            item['subway'] = subway.strip()
            details = room.xpath('.//div[@class="detail"]/p[1]/span/text()')
            item['area'], item['floor'], item['room_type'], item['rental_type'] = details
            item['room_tags'] = room.xpath('.//p[@class="room_tags clearfix"]//span/text()')
            item['price'] = room.xpath('.//p[@class="price"]/text()')[0].strip()
            self.store_room(item)

    def find_rooms(self):
        self.get_index_urls()

        while not self.request_q.empty():
            requests = cut_queue(self.request_q, self.concurrent_num)
            resps = grequests.map(requests, gtimeout=self.gtimeout)
            for index, resp in enumerate(resps):
                if not resp:  # 重新放入队列
                    self.request_q.put(requests[index])
                    continue
                self.get_room_url(resp)

        self.off_sell()

    def store_room(self, item):
        self.after_room_ids.add(item['room_id'])
        item['sell_status'] = 'on'
        self.db.ziroom.update_one(
            {'room_id': item['room_id']},
            {'$set': item},
            upsert=True
        )

    def off_sell(self):
        off_set = set(self.before_room_ids) - self.after_room_ids
        for room_id in off_set:
            self.db.ziroom.update_one(
                {'room_id': room_id},
                {'$set': {'sell_status': 'off'}}
            )

    def add_location(self, city=None):
        # 调用api获取房间location
        city = city or self.city
        not_exist_num = 0  # 有的地址用api搜不到，可能搜索信息不完整，需要手动并入库
        request_q = Queue()

        for room in self.db.ziroom.find(
                {'location': None}, {'address': 1, 'district': 1}
        ):
            address = room['district'] + room['address']
            url = self.location_url.format(choice(self.keys), address, city)
            attrs = {'room_id': ObjectId(room['_id'])}
            request_q.put(request(url, is_map=True, attrs=attrs))

        while not request_q.empty():
            requests = cut_queue(request_q, self.concurrent_num)
            resps = grequests.map(requests, gtimeout=self.gtimeout)
            for index, resp in enumerate(resps):
                try:
                    matched = resp.json()['geocodes'][0]
                    coordinates = [
                        float(i) for i in matched['location'].split(',')
                    ]
                    location = {'type': 'Point', 'coordinates': coordinates}
                except:
                    not_exist_num += 1
                    logger.error('error, cannot find %s', not_exist_num)
                    logger.error(requests[index].url)
                    continue
                self.db.ziroom.update_one(
                    {'_id': requests[index].room_id},
                    {
                        '$set': {
                            'location': location,
                            'formatted_address': matched['formatted_address'],
                            'province': matched['province'],
                            'city': matched['city'],
                            'district': matched['district'],
                            'street': matched['street']
                        },
                        '$unset': {'address': 1}
                    }
                )

    def search_rooms(self, destination, dis=0.3, dur=0.3, pro=0.4, distance=10):
        """
        查找给定范围内的房间，通过api为房间添加繁华程度，计算房间与目的地之间距离，耗时
        :param destination: str 'longitude,latitude'
        :param dis: distance weight
        :param dur: duration weight
        :param pro: prosperous level weight
        :param distance: 目的地周边范围　KM
        :return:
        """
        # search_result = []      # 最终结果
        # room_loc_q = Queue()    # 房间location
        # id_q = Queue()          # 更新数据库
        distance_q = Queue()    # 请求起点终点距离，花费时间
        prosperous_q = Queue()  # 请求某地繁华程度

        dest = [float(i) for i in destination.split(',')]
        rooms = self.db.ziroom.find(
            {
                'location': {
                    '$near': {
                        '$geometry': {
                            'type': 'Point',
                            'coordinates': dest
                        },
                        '$maxDistance': distance * 1000
                    }
                },
                'sell_status': 'on'
            },
            {'location': 1}
        )
        print('find rooms: ', rooms.count())
        for room in rooms:
            location = ','.join([str(i) for i in room['location']['coordinates']])
            url = self.distance_url.format(
                choice(self.keys), location, destination
            )
            attrs = {'room_id': ObjectId(room['_id'])}
            distance_q.put(request(url, is_map=True, attrs=attrs))

            if not room.get('prosperous_level'):
                # 如果没有，则请求添加
                url = self.prosperous_url.format(choice(self.keys), location)
                prosperous_q.put(request(url, is_map=True, attrs=attrs))

        t1 = time()
        # self.add_prosperous(prosperous_q)
        # t2 = time()
        # print('add prosperous done', t2-t1)
        results = self.get_distance(distance_q)
        t3 = time()
        print('get distance done', t3-t1)

        # origins 最多支持100个
        # while not room_loc_q.empty():
        #     locations = cut_queue(room_loc_q, 50)
        #     _ids = cut_queue(id_q, 50)
        #     origins = '|'.join(locations)
        #     url = self.distance_url.format(
        #         choice(self.keys), origins, destination
        #     )
        #     attrs = {'room_ids': _ids}
        #     distance_q.put(request(url, is_map=True, attrs=attrs))
        #
        # while not distance_q.empty():
        #     requests = cut_queue(distance_q, self.concurrent_num)
        #     resps = grequests.map(requests, gtimeout=self.gtimeout)
        #     for index, resp in enumerate(resps):
        #         # num = resp.url.count('|') + 1
        #         _ids = requests[index].room_ids
        #         resp = resp.json()
        #         # _ids = cut_queue(id_q, num)
        #         if int(resp['infocode']) != 10000:
        #             logger.error('error, infocode: %s', resp['infocode'])
        #             distance_q.put(requests[index])
        #             # for _id in _ids:
        #             #     id_q.put(_id)
        #             continue
        #         for i, result in enumerate(resp['results']):
        #             distance, duration = result['distance'], result['duration']
        #
        #             room = self.db.ziroom.find_one(
        #                 {'_id': _ids[int(result['origin_id'].strip('"'))-1]},
        #                 {'prosperous_level': 1, 'room_url': 1, '_id': 0}
        #             )
        #             search_result.append([
        #                 room['room_url'], distance,
        #                 duration, room['prosperous_level']
        #             ])

        # 归一化
        dis_mid, dis_asd = self.calc_mid_asd(results, key=1)
        dur_mid, dur_asd = self.calc_mid_asd(results, key=2)
        pro_mid, pro_asd = self.calc_mid_asd(results, key=3)
        print(dis_mid, dis_asd)
        print(dur_mid, dur_asd)
        print(pro_mid, pro_asd)

        for result in results:
            dis_score = (result[1] - dis_mid) / dis_asd
            dur_score = (result[2] - dur_mid) / dur_asd
            pro_score = (result[3] - pro_mid) / pro_asd
            result.append(round(dis_score, 2))
            result.append(round(dur_score, 2))
            result.append(round(pro_score, 2))
            result.append(round(dur_score*dur+dis_score*dis+pro_score*pro, 2))
        # dis_ = self.normalization(results, 1)
        # dur_ = self.normalization(results, 2)
        # pro_ = self.normalization(results, 3)
        #
        # for index, result in enumerate(results):
        #     result.append(dis_[index])
        #     result.append(dur_[index])
        #     result.append(pro_[index])
        #     result.append(dis_[index]*dis+dur_[index]*dur+pro_[index]*pro)

        print('calculate done', time()-t3)
        for result in sorted(results, key=itemgetter(-1), reverse=True):
            print(result)

    def add_prosperous(self, prosperous_q):
        while not prosperous_q.empty():
            requests = cut_queue(prosperous_q, self.concurrent_num)
            resps = grequests.map(requests, gtimeout=self.gtimeout)
            for index, resp in enumerate(resps):
                if not resp:
                    logger.error('recycle %s', requests[index].url)
                    prosperous_q.put(requests[index])
                    continue
                resp = resp.json()
                if int(resp['infocode']) != 10000:
                    logger.error('error, update infocode: ', resp['infocode'])
                    prosperous_q.put(requests[index])
                    continue

                self.db.ziroom.update_one(
                    {'_id': requests[index].room_id},
                    {'$set': {'prosperous_level': int(resp['count'])}}
                )

    def get_distance(self, distance_q):
        results = []
        while not distance_q.empty():
            requests = cut_queue(distance_q, self.concurrent_num)
            resps = grequests.map(requests, gtimeout=self.gtimeout)
            for index, resp in enumerate(resps):
                if not resp:
                    distance_q.put(requests[index])
                    continue
                resp = resp.json()
                if int(resp['infocode']) != 10000:
                    logger.error('error, infocode: %s', resp['infocode'])
                    logger.error(requests[index].url)
                    distance_q.put(requests[index])
                    continue
                result = resp['results'][0]
                distance, duration = result['distance'], result['duration']

                room = self.db.ziroom.find_one(
                    {'_id': requests[index].room_id},
                    {'prosperous_level': 1, 'room_url': 1, '_id': 0}
                )
                results.append([
                    room['room_url'], int(distance),
                    int(duration), room['prosperous_level']
                ])
        return results

    # def normalization(self, seq, key):
    #     seq = [i[key] for i in seq]
    #     distance = max(seq) - min(seq)
    #     result = []
    #     for i in seq:
    #         value = (i - min(seq)) / distance
    #         if value == 0:
    #             result.append(1)
    #         elif value == 1:
    #             result.append(0)
    #         else:
    #             result.append(round(1/distance, 2))
    #     return result

    def calc_mid_asd(self, seq, key):
        # 计算中位数，绝对标准差
        _sort = sorted(seq, key=itemgetter(key))
        mid = _sort[len(_sort)//2+1][key]
        if len(_sort) % 2 == 1:
            middle = mid
        else:
            middle = (mid + _sort[len(_sort)//2][key]) / 2
        return middle, sum([abs(i[key]-middle) for i in _sort])/len(_sort)


if __name__ == '__main__':
    ziroom = Ziroom()
    # ziroom.find_rooms()
    #
    # ziroom.add_location()

    destination_url = 'http://restapi.amap.com/v3/geocode/geo?key=1f6d0d8ea68c21088beec7e0ca5e7b1e&address=方恒国际中心A座&city=北京'
    destination = request(destination_url).json()['geocodes'][0]['location']
    ziroom.search_rooms(destination)

