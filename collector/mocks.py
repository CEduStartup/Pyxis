from config import logger

GENERIC_HANDLER = 'GenericHandler'

class GenericHandler(object):
    def process_data(self, data):
        """ Processes data, passed from url response. """
        'Data processed by GenericHandler'

class TaskModel(object):
    @staticmethod
    def get_tasks():
        return [
            dict(duration=5,  url='http://www.google.com',        handler=GENERIC_HANDLER),
            dict(duration=4,  url='http://www.msn.com',           handler=GENERIC_HANDLER),
            dict(duration=3,  url='http://www.developers.org.ua', handler=GENERIC_HANDLER),
            dict(duration=8,  url='http://www.habrahabr.ru',      handler=GENERIC_HANDLER),
            dict(duration=10, url='http://news.bigmir.net',       handler=GENERIC_HANDLER)
        ]
            
        