from wsgiref.simple_server import make_server
import json
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
    '/get', 'get'
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
                            'alive_times': {'$gt': 5},
                            'type': {'$in': ['high']},
                            'protocol': {
                                '$in': [protocol.get('protocol', 'http')]
                            }
                         },
                        {'proxy': 1, '_id': 0}
                    ).limit(int(count.get('count', 50)))]
        return json.dumps(results)


if __name__ == "__main__":
    app.run()


# for i in COLLECTION.find({'detect_times': {'$gt': 5}}):
#     if not i.get('alive_times'):
#         s = COLLECTION.find_one_and_delete({'_id': i.get('_id')})
#         print(s.get('proxy'))
#
# for i in COLLECTION.find(
#                 {'alive_times': {'$gt': 5}, 'type': {'$in': ['high']}},
#                 {'proxy': 1, '_id': 0}
#             ).limit(50):
#     print(i)