import os
import tornado.httpserver
import tornado.web
from tornado import autoreload
import tornadio2

class LoggerConnection(tornadio2.SocketConnection):
    connections = set()
    
    def on_open(self, info):
        print '>> CONNECTED', info
        self.connections.add(self)
        
    def on_close(self):
        print '<< DISCONNECTED'
        self.connections.remove(self)
    
    def on_event(self, name, *args, **kwargs):
        if name == 'connected':
            self.emit('log', msg='Just a message')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        static_path = os.path.join(base_dir, "static")
        handlers = [
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path }),
            (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": static_path })
        ]
        
        def print_callback():
            for conn in LoggerConnection.connections:
                conn.emit('log', msg='Just a message')

        tornado.ioloop.PeriodicCallback(print_callback, 1000).start()
        
        LoggerServer = tornadio2.router.TornadioRouter(LoggerConnection)
        handlers.extend(LoggerServer.urls)
        settings = dict(
            static_path=static_path,
            template_path=os.path.join(base_dir, "templates"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(9998)
    
    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(ioloop)
    ioloop.start()
    