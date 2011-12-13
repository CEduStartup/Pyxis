import sys
import os
import shutil
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


DEFAULT_WEB_LOGGER_PORT = 9997
LOG_FILENAME = os.path.join(os.path.dirname(__file__), '../logs/logger.log')

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
        print 'got event %s, %s, %s' % (name, args, kwargs)
        if name == 'console_config':
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
                                     type=event.component)
        except Queue.Empty:
            pass
    
class LogFile(object):
    """This class implements log file behavior with log aggregation by date."""
    
    def __init__(self, filename):
        if os.path.isfile(filename):
            (_filename, _ext) = os.path.splitext(filename)
            aggr_filename = "%s_%s%s" % (_filename, datetime.now().strftime('%Y%m%d'), _ext)
            if os.path.isfile(aggr_filename):
                src = open(filename)
                dst = open(aggr_filename, 'a')
                try:
                    shutil.copyfileobj(src, dst)
                finally:
                    src.close()
                    dst.close()
            else:
                shutil.move(filename, aggr_filename)
        self.f = open(filename, 'w')
        
    def push(self, log_message):
        self.f.write("%s\n" % (log_message,))
        self.f.flush()

class EventReceiverThread(mp.Process):
    """This thread is runned as a process, and interacts with tornado server using queue.
    It starts EventReceiver, which puts new events to the queue."""
    
    # Queue to pass log events to
    log_queue = None
    
    # Queue to receive commands from parent process 
    control_queue = None
    
    config = None
    
    def __init__(self, log_queue = None, control_queue = None, log_file=None, config={}):

        mp.Process.__init__(self, target=self._run)
        self.log_queue = log_queue
        self.control_queue = control_queue
        self.log_file = log_file
        self.config = {'show_console_log': 0}
        self.config.update(config)
        
        self.receiver = EventReceiver(server_host=queue_host,
                                      server_port=queue_port,
                                      tubes=(LOGGER_TUBE,),
                                      callback=self.on_message)

    def on_message(self, event):
        self.check_control_queue()
        self.log_queue.put_nowait(event)
        log_msg = '[ %s ] - %s [ %s ] %s' % (
           event.tags[1].upper(), # Component name.
           datetime.fromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S'),
           event.level.upper(),
           event.format_message())
        self.log_file.push(log_msg)
        if self.config['show_console_log']:
            print log_msg

    def check_control_queue(self):
        """Checks control queue for new commands from parent process and process them."""
        try:
            while True:
                cmd = self.control_queue.get_nowait()
                self.process_cmd(cmd)
        except Queue.Empty:
            pass

    def process_cmd(self, cmd):
        pass

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

def main():
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = DEFAULT_WEB_LOGGER_PORT
    
    receiver_config = {}
    if '--console' in sys.argv:
        receiver_config['show_console_log'] = True
    
    print 'Starting Web-based Logger manager on port %s' % port
    log_queue     = mp.Queue()
    control_queue = mp.Queue()

    # tornado web-server initialization
    server = tornado.httpserver.HTTPServer(Application(log_queue))
    server.listen(port)

    ioloop = tornado.ioloop.IOLoop.instance()
    # autoreload for debug
    autoreload.start(ioloop)

    log_file = LogFile(LOG_FILENAME)


    EventReceiverThread(log_queue=log_queue, control_queue=control_queue, log_file=log_file, config=receiver_config).start()

    #starting tornado's event loop
    ioloop.start()

if __name__ == "__main__":
    main(port)
