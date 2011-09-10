from config import logger

class Worker(object):
    def process_task(self, task):
        logger.info('Processing task %s' % task)
    