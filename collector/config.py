from datetime import datetime
import sys

class Logger(object):
    log_levels = [] # Empty means all
    
    def __init__(self):
        log_levels = [arg for arg in sys.argv if arg[:13] == '--log_levels=']
        if log_levels: 
            self.log_levels = log_levels[0][13:].split(',')
    
    def _msg(self, tag, msg):
        # Nothing more for now :)
        if not self.log_levels or tag in self.log_levels:
            print "%s [%s] %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tag, msg)
        
    def info(self, msg):
        return self._msg('info', msg)

    def warn(self, msg):
        return self._msg('warn', msg)

logger = Logger()
