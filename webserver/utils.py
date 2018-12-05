import json
from webserver.server import MyWebServer


def jsonify(**kwargs):
    content = json.dumps(kwargs)
    return MyWebServer.Request(content, '200 OK', content_type='application/json', charset='utf-8')
