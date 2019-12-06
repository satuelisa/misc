#!/usr/bin/python
import tornado.ioloop
import tornado.web
import tornado.websocket
import datetime
from tornado.options import define, options, parse_command_line
from sys import stderr

define("port", default=8888, help="run on the given port", type=int)
clients = dict()

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        source = self.request.remote_ip
        self.write("Connected.")
        self.finish()

    def check_origin(self, origin):
        return True

def compute(count, target=None):
    found = 0
    cand = 0
    while found < count:
        cand += 1
        if cand == 1:
            target.write_message(cand)
            found += 1
        elif cand % 2 == 0:
            if cand == 2:
                target.write_message(cand)
                found += 1
        else:
            start = cand + 2
            end = cand - 2
            ok = True
            for div in xrange(start, cand, 2):
                if cand % div == 0:
                    ok = False
                    break
            if ok:
                target.write_message(cand)
            found += 1

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        source = self.request.remote_ip
        n = self.get_argument("count")
        self.stream.set_nodelay(True)
        compute(n, self);
        self.close()

    def on_message(self, msg):
        return

    def on_close(self):
        return

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/prime', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

