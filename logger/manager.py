from datetime import datetime
from config.mq import queue_host, queue_port
from shared.events.EventManager import EventReceiver
from shared.events.Event import BaseEvent, LOGGER_TUBE

class LogManager:

    """Log manager which listens for logger events and shows them on the screen.

    Now provides possibility just to show all logs.
    FUTURE: possibility to filter by some rules
    """

    def __init__(self, queue_host, queue_port):
        self.receiver = EventReceiver(server_host=queue_host,
                                      server_port=queue_port,
                                      tubes=(LOGGER_TUBE,),
                                      callback=self.on_message)

    def start(self):
        self.receiver.dispatch()

    def on_message(self, event):
        if isinstance(event, BaseEvent):
            log_msg = '[ %s ] - %s [ %s ] %s' % (
               event.tags[1].upper(), # Component name.
               datetime.fromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S'),
               event.level.upper(),
               event.msg)
            print log_msg


if __name__ == '__main__':
    LogManager(queue_host, queue_port).start()




