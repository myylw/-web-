import json
from webserver.server import MyWebServer


def jsonify(**kwargs):
    content = json.dumps(kwargs)
    # print(content)
    config = {'text': content,
              'status': '200',
              'content_type': 'application/json',
              'charset': 'utf-8'}

    return MyWebServer.Response(**config)
