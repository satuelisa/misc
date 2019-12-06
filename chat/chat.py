#!/usr/bin/python
import tornado.ioloop
import tornado.web
import tornado.websocket
import datetime
from tornado.options import define, options, parse_command_line
from sys import stderr

define("port", default=8080, help="run on the given port", type=int)
clients = dict()
lights = dict()

admin = ["189.205.106.84", "148.234.44.208", "127.0.0.1", "148.234.195.15"]
local = "192.168"
fime = "148.234.32"
wuanl = "148.234.21"

def timerange():
    day = datetime.datetime.today().weekday()
    if day < 6 and day % 2 == 0: # Monday, Wednesday, Friday:
        return (datetime.time(14, 15, 0) 
                <= datetime.datetime.now().time() 
                <= datetime.time(17, 05, 0))
    return False

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        source = self.request.remote_ip
        auth = False
        if source in admin or local in source:
            auth = True
        elif fime in source or wuanl in source: 
            auth = timerange()
        if auth:
            self.write("Origen autorizada.")
        #self.render("index.html")
        self.finish()

    def check_origin(self, origin):
        return True

def compute(target=None):
    r = 0
    y = 0
    g = 0
    for l in lights.values():
        if 'r' in l:
            r += 1
        elif 'y' in l:
            y += 1
        elif 'g' in l:
            g += 1
    if r + y + g > 0:
        status = '%d %d %d\n' % (r, y, g)
        if target is None:
            for c in clients.values():
                c.write_message(status)
        else:
            target.write_message(status)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        source = self.request.remote_ip
        auth = False
        if source in admin or local in source:
            auth = True
        elif fime in source or wuanl in source:
            auth = timerange()
        if auth:
            self.ident = self.get_argument("student")
            self.stream.set_nodelay(True)
            clients[self.ident] = self
            self.write_message('<span style="color:Chartreuse">[Conectado al chat.]</span>')
            compute(self);
        else:
            self.write_message('<span style="color:yellow">[Este chat funciona solamente en clase, LMV 14:30-17:00.]</span>')
            self.close()

    def on_message(self, msg):
        if '[' in msg:
            for ident in clients:
                c = clients[ident]
                if c != self:
                    c.write_message(msg)
        else:
            lights[self.ident] = msg;
            compute();

    def on_close(self):
        if self.ident in clients:
            del clients[self.ident]
            del lights[self.ident]
            compute()

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/chat', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

