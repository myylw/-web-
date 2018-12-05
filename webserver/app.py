from wsgiref.simple_server import make_server
from webserver.server import MyWebServer
from webob import Request, Response


product = MyWebServer.Router('/idtest')
MyWebServer.register(product)


@product.get('/{id:int}')
def id_test(ctx, request: Request):
    res = Response()
    res.content_type = 'text/plain'
    res.text = f'id = {request.vars.id}'
    return res


if __name__ == '__main__':
    ip, port = '127.0.0.1', 8888
    server = make_server(ip, port, MyWebServer())
    server.serve_forever()
