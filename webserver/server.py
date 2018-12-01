from wsgiref.simple_server import make_server
from webob import Request, exc, Response
from webob.dec import wsgify
import re


class DictObj:
    def __init__(self, d: dict):
        if not isinstance(d, dict):
            self.__dict__['_dict'] = {}
        else:
            self.__dict__['_dict'] = d

    def __getattr__(self, item):
        try:
            return self._dict[item]
        except KeyError:
            raise AttributeError()

    def __setattr__(self, key, value):
        raise NotImplementedError()


class Context(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError()

    def __setattr__(self, key, value):
        self[key] = value


class NestedContext(Context):
    def __init__(self, globalcontext: Context = None):
        super().__init__()
        self.relate(globalcontext)

    def relate(self, globalcontext: Context = None):
        self.globalcontext = globalcontext

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        return self.globalcontext[item]


class Router:
    TYPEPATTERN = {
        'str': r'[^/]+',
        'int': r'[+-]?\d+',
        'float': r'[+-]?\d+\.\d+',
        'any': r'.+'
    }

    TYPECAST = {
        'str': str,
        'int': int,
        'float': float,
        'any': str
    }

    KVPATTERN = re.compile(r'/({[^{}:]+:?[^{}:]*})')

    def _transform(self, kv: str):
        name, _, type = kv.strip('/{}').partition(':')
        return '/(?P<{}>{})'.format(name, self.TYPEPATTERN.get(type, '\w+')), name, self.TYPECAST.get(type, str)

    def _parse(self, src: str):
        start = 0
        res = ''
        translator = {}
        while True:
            matcher = self.KVPATTERN.search(src, start)
            if matcher:
                res += matcher.string[start:matcher.start()]
                tmp = self._transform(matcher.string[matcher.start():matcher.end()])
                res += tmp[0]
                translator[tmp[1]] = tmp[2]
                start = matcher.end()
            else:
                break
        if res:
            return res, translator
        else:
            return src, translator

    def __init__(self, prefix: str = ''):
        self.__prefix = prefix.rstrip('/\\')
        self.__routetable = []
        self.ctx = NestedContext()

    @property
    def prefix(self):
        return self.__prefix

    def route(self, rule, *methods):
        def wrapper(handler):
            pattern, translator = self._parse(rule)
            self.__routetable.append((methods, re.compile(pattern), translator, handler))
            return handler

        return wrapper

    def get(self, pattern):
        return self.route(pattern, 'GET')

    def post(self, pattern):
        return self.route(pattern, 'POST')

    def head(self, pattern):
        return self.route(pattern, 'HEAD')

    def match(self, request: Request):
        if not request.path.startswith(self.__prefix):
            return None

        for methods, pattern, translator, handler in self.__routetable:
            if not methods or request.method.upper() in methods:
                matcher = pattern.match(request.path.replace(self.__prefix, '', 1))
                if matcher:
                    newdict = {}
                    for k, v in matcher.groupdict().items():
                        newdict[k] = translator[k](v)
                    request.vars = DictObj(newdict)
                    response = handler(self.ctx, request)

                return response


class Application:
    ctx = Context()

    def __init__(self, **kwargs):
        self.ctx.app = self
        for k, v in kwargs:
            self.ctx[k] = v

    ROUTERS = []

    @classmethod
    def register(cls, router: Router):
        router.ctx.relate(cls.ctx)
        router.ctx.router = router
        cls.ROUTERS.append(router)

    @wsgify
    def __call__(self, request):
        for router in self.ROUTERS:
            print(request)
            response = router.match(request)

            if response:
                return response

        raise exc.HTTPNotFound()

    @classmethod
    def extend(cls, name, plugin):
        cls.ctx[name] = plugin


index = Router('/')
Application.register(index)


@index.get('/')
def index_test(ctx, request: Request):
    print(ctx)
    print(request)

    res = Response()
    res.status_code = 200
    res.charset = 'utf-8'
    res.body = '<h1>test</h1>'.encode()
    return res


if __name__ == '__main__':
    ip, port = '127.0.0.1', 8888
    server = make_server(ip, port, Application())
    server.serve_forever()
