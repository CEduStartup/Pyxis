def method(*args, **kwargs):
    pass

class Logger:
    def __getattr__(self, *args, **kwargs):
        return method

logger = Logger()
