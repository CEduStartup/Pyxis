import sys
import os
import tornado.httpserver
import tornado.web
from tornado import autoreload
import tornadio2
import time
import Queue
from datetime import datetime

import multiprocessing as mp

import config.logger as logger_config

from config.mq import queue_host, queue_port
from shared.events.EventManager import EventReceiver
from shared.events.Event import BaseEvent, LOGGER_TUBE


class LoggerConnection(tornadio2.SocketConnection):
    connections = set()

    def on_open(self, info):
        self.connections.add(self)

    def on_close(self):
        self.connections.remove(self)

    def on_event(self, name, *args, **kwargs):
        if name == 'connected':
            self.emit('log', msg='Just a message')
        if name == 'config':
            pass


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class EventCallback(object):
    queue=None

    def __init__(self, queue):
        self.queue=queue

    def __call__(self):
        try:
            while True:
                event = self.queue.get_nowait()
                for conn in LoggerConnection.connections:
                    conn.emit('log', time=datetime.fromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S'),
                                     msg=event.format_message(),
                                     level=event.level,
                                     type=event.component)
        except Queue.Empty:
            pass


class EventReceiverThread(mp.Process):
    queue = None

    def __init__(self, queue=None):
        mp.Process.__init__(self, target=self._run)
        self.queue = queue
        self.receiver = EventReceiver(server_host=queue_host,
                                      server_port=queue_port,
                                      tubes=(LOGGER_TUBE,),
                                      callback=self.on_message)

    def on_message(self, event):
        #print "[%d\t] %s" % (self.queue.qsize(), event.format_message())
        self.queue.put_nowait(event)

    def _run(self):
        self.receiver.dispatch()


class Application(tornado.web.Application):
    def __init__(self, queue):
        base_dir = os.path.dirname(__file__)
        static_path = os.path.join(base_dir, "static")
        handlers = [
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path }),
            (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": static_path })
        ]

        tornado.ioloop.PeriodicCallback(EventCallback(queue=queue), 10).start()

        LoggerServer = tornadio2.router.TornadioRouter(LoggerConnection)
        handlers.extend(LoggerServer.urls)
        settings = dict(
            static_path=static_path,
            template_path=os.path.join(base_dir, "templates"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main(port=9997):
    print 'Starting Web-based Logger manager on port %s' % port
    queue = mp.Queue()

    server = tornado.httpserver.HTTPServer(Application(queue))
    server.listen(port)

    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(ioloop)

    EventReceiverThread(queue=queue).start()
    ioloop.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9997
    main(port=port)
