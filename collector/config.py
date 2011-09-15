from datetime import datetime

class Logger(object):
    def _msg(self, tag, msg):
        # Nothing more for now :)
        print "%s [%s] %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tag, msg)
        
    def info(self, msg):
        return self._msg('info', msg)

    def warn(self, msg):
        return self._msg('warn', msg)

logger = Logger()
