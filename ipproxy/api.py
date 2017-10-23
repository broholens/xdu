from wsgiref.simple_server import make_server
import json
import pymongo
from ipproxy.settings import COLLECTION
import web


# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/json')])
#     results = [i.get('proxy') for i in COLLECTION.find(
#                 {'alive_times': {'$gt': 5}, 'type': {'$in': ['high']}},
#                 {'proxy': 1, '_id': 0}
#             ).limit(50)]
#     return json.dumps(results)
#
#
# httpd = make_server('', 8000, application)
# print('ok---')
# httpd.serve_forever()


urls = (
    '/', 'index',
    '/get', 'get',
    '/increase_detect_times', 'detect',
    '/increase_alive_times', 'alive'
)
app = web.application(urls, globals())


class index:
    def GET(self):
        return 'try http://0.0.0.0:8080/get?count=50&protocol=http'


class get:
    def GET(self):
        count, protocol = web.input(), web.input()
        results = [i.get('proxy') for i in COLLECTION.find(
                        {
                            'score': {'$gt': 0.8},
                            'protocol': {
                                '$in': [protocol.get('protocol', 'http')]
                            }
                         },
                        {'proxy': 1, '_id': 0}
                    ).sort('alive_times', pymongo.DESCENDING)]
        #  ).limit(int(count.get('count', 50)))]
        return json.dumps(results)


class detect:
    def POST(self):
        COLLECTION.update_one(
            {'proxy': json.loads(web.data())},
            {'$inc': {'detect_times': 1}}
        )


class alive:
    def POST(self):
        COLLECTION.update_one(
            {'proxy': json.loads(web.data())},
            {'$inc': {'alive_times': 1, 'detect_times': 1}}
        )


if __name__ == "__main__":
    app.run()

