class Logger(object):
    def _msg(self, tag, msg):
        # Nothing more for now :)
        print "[%s] %s" % (tag, msg)
        
    def info(self, msg):
        return self._msg('info', msg)

logger = Logger()