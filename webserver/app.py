from wsgiref.simple_server import make_server
from webserver.server import MyWebServer
from webob import Request, Response
from webserver import utils

# router
test = MyWebServer.Router('/idtest')
test2 = MyWebServer.Router('/test2')
test3 = MyWebServer.Router('/json_test')

# reg router
MyWebServer.register(test)
MyWebServer.register(test2)
MyWebServer.register(test3)


@test.get('/{id:int}')
def id_test(ctx, request: Request):
    res = Response()
    res.content_type = 'text/plain'
    res.text = f'id = {request.vars.id}'
    return res


@test2.get('')
def interceptor_test(ctx, req: Request):
    res = Response()
    res.content_type = 'text/plain'
    res.text = 'interceptor test'
    return res


@test2.register_preinterceptor
def pre_interceptor(ctx, req):
    print('interceptor is working')
    return req


@test3.post('')
def js_request(ctx, req):
    print(req.text)
    return utils.jsonify(test='jsonify')


if __name__ == '__main__':
    ip, port = '127.0.0.1', 8888
    server = make_server(ip, port, MyWebServer())
    server.serve_forever()
