from shared.events.EventManager import EventReceiver
from datetime import datetime
from shared.events.Event import LOGGER_TUBE

class LogManager:
    
    """ Log manager which listens for logger events and shows them on the screen. 
    
    Now provides possibility just to show all logs.
    FUTURE: possibility to filter by some rules        
    """
    
    def __init__(self):
        self.receiver = EventReceiver(tubes=(LOGGER_TUBE,), callback=self.on_message)
    
    def start(self):
        self.receiver.dispatch()
        
    def on_message(self, event):
        log_msg = '%s [ %s ] %s' % (datetime.fromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S'),
                                    event.eid.split('.').pop().upper(),
                                    event.msg)
        print log_msg
    
    
if __name__ == '__main__':
    LogManager().start()




