from queue import Queue
from string import ascii_uppercase
from multiprocessing import JoinableQueue, Process

from pymongo import MongoClient, TEXT
from bson.objectid import ObjectId

from ipproxy import utils


class Tutor:

    base_url = 'http://web.xidian.edu.cn'

    def __init__(self):
        self.logger = utils.logger
        self.col = MongoClient().tutor.tutor

    def _put_to_homepage_q(self):
        for i in ascii_uppercase:
            self.homepage_q.put(self.base_url+f'/searchbychar.php?char={i}')

    def get_tutors(self):
        # https://docs.mongodb.com/manual/tutorial/text-search-with-rlp/
        # self.col.create_index([('speciality_text', TEXT)],
        #                       default_language='simplified chinese')
        self.homepage_q = Queue()
        self._put_to_homepage_q()
        self.speciality_q = JoinableQueue()
        p1 = Process(target=self._get_homepage)
        p2 = Process(target=self._get_speciality)
        p2.daemon = True
        p1.start()
        p2.start()
        p1.join()

    def _get_homepage(self):
        while not self.homepage_q.empty():
            url = self.homepage_q.get()
            resp = utils.request(url)
            self._parse_homepage(resp, url)
        self.speciality_q.join()

    def _get_speciality(self):
        while True:
            url = self.speciality_q.get()
            resp = utils.request(url)
            self._parse_speciality(resp, url)
            self.speciality_q.task_done()

    def _parse_homepage(self, response, url):
        teachers = self._parse(response, 'homepage', url)
        if not teachers:
            return

        for teacher in teachers:
            teacher_url = utils.xpath_extract(teacher, './a/@href', True)
            teacher_name = utils.xpath_extract(teacher, './a/text()', True)
            if teacher_url and teacher_name:
                self.logger.info('find teacher %s', teacher_name)
                self.speciality_q.put(self.base_url+teacher_url)
                self.col.update_one(
                    {'homepage_url': self.base_url+teacher_url},
                    {
                        '$set': {
                            'homepage_url': self.base_url+teacher_url,
                            'tutor_name': teacher_name
                        }
                    },
                    upsert=True
                )
            else:
                self.logger.error('cannot find tutors %s', response.url)

    def _parse_speciality(self, response, url):
        specialities = self._parse(response, 'speciality', url)
        if not specialities:
            return

        specialities = ''.join(specialities)
        self.col.update_one(
            {'homepage_url': response.url.rstrip('/')},
            {
                '$set': {'speciality_text': specialities}
            },
            upsert=True
        )

    def _parse(self, response, label, url):
        q = self.homepage_q if label == 'homepage' else self.speciality_q
        if not response:
            self.logger.error('failed to fetch %s', url)
            q.put(url)
            return

        self.logger.info('fetched %s', response.url)
        tree = utils.to_tree(response.text)
        if not tree:
            self.logger.error('to tree error %s', response.url)
            return

        if utils.xpath_extract(tree, '//head/title/text()', True) == '网站防火墙':
            self.logger.error('网站防火墙 +_+ %s', response.url)
            q.put(response.url)
            return

        if label == 'homepage':
            return utils.xpath_extract(tree, '//ul[@id="left_ul"]/li')

        return utils.xpath_extract(tree, '//div[@class="nr"]//text()')
        # utils.xpath_extract(tree, '//div[@id="n2"]//text()')

        # if not results:
        #     self.logger.error('cannot parse %s', response.url)
        #     q.put(response.url)

        # return results

    def search(self, speciality):
        print('searching......')
        # tutors = self.col.find(
        #     {'$text': {'$search': speciality, '$language': 'hans'}},
        #     {'speciality_text': 0}
        # )
        # num_tutors = tutors.count()
        # if num_tutors == 0:
        #     print(f'not find tutors research {speciality}')
        #     return
        # print(f'find {num_tutors} tutors research {speciality}')
        tutor_num = 0
        for tutor in self.col.find():
            if speciality not in tutor.get('speciality_text', ''):
                continue
            tutor_num += 1
            print(tutor_num, tutor['tutor_name'], tutor['homepage_url'])
            # TODO: how to use this
            self.col.update_one(
                {'_id': ObjectId(tutor['_id'])},
                {'$setOnInsert': {'specialities': speciality}},
                upsert=True
            )
        if tutor_num == 0:
            print(f'not find tutor research {speciality}')


if __name__ == '__main__':
    tutors = Tutor()
    # tutors.get_tutors()
    tutors.search('深度')
