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

from config.mq import queue_host, queue_port
from shared.events.EventManager import EventReceiver
from shared.events.Event import BaseEvent, LOGGER_TUBE


DEFAULT_WEB_LOGGER_PORT = 9997

class LoggerConnection(tornadio2.SocketConnection):
    """This class represents socket.io connection and stores all connected clients 
    in `connections` attribute."""
    
    connections = set()
    
    def on_open(self, info):
        """Method is called by tornadio, when connection created. Stores current connection to 
        `connections` set."""
        self.connections.add(self)
        
    def on_close(self):
        """Method is called by tornadio, when client disconnected. Removes connection from
        list of active connections."""
        self.connections.remove(self)
    
    def on_event(self, name, *args, **kwargs):
        """Event handler for event from the client.
        
        When client sends a message, tornadio calls this method for particular connection."""
        if name == 'config':
            pass


class IndexHandler(tornado.web.RequestHandler):
    """This handler processes request to '/'."""
    def get(self):
        self.render('index.html')


class EventCallback(object):
    """This callback is called by tornado every n ms. By calling it queue is checked, and 
    if any new event exist, they are sent to all connected clients."""
    
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
                                     type=event.tags[-1])        
        except Queue.Empty:
            pass
    

class EventReceiverThread(mp.Process):
    """This thread is runned as a process, and interacts with tornado server using queue.
    It starts EventReceiver, which puts new events to the queue."""
    
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
    """Web-server application."""
    
    EVENT_CALLBACK_PERIOD = 10 # ms
        
    def __init__(self, queue):
        """Initializes web-server configurations.
        
        1. Adds handler for '/' request, which returns rendered index.html template.
        2. Adds standard handlers for static files
        3. Setups tornado's periodic callback for event queue check
        4. Setups routes to socket.io request handlers using tornadio2 library
        """
        
        base_dir = os.path.dirname(__file__)
        static_path = os.path.join(base_dir, "static")
        handlers = [
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path }),
            (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": static_path })
        ]
        
        tornado.ioloop.PeriodicCallback(EventCallback(queue=queue), Application.EVENT_CALLBACK_PERIOD).start()
        
        LoggerServer = tornadio2.router.TornadioRouter(LoggerConnection)
        handlers.extend(LoggerServer.urls)
        settings = dict(
            static_path=static_path,
            template_path=os.path.join(base_dir, "templates"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main(port):
    print 'Starting Web-based Logger manager on port %s' % port
    queue = mp.Queue()
    
    # tornado web-server initialization
    server = tornado.httpserver.HTTPServer(Application(queue))
    server.listen(port)
    
    ioloop = tornado.ioloop.IOLoop.instance()
    # autoreload for debug 
    autoreload.start(ioloop)

    # starting event receiver process
    EventReceiverThread(queue=queue).start()
    
    #starting tornado's event loop
    ioloop.start()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WEB_LOGGER_PORT
    main(port)