from config import logger
from mocks import TaskModel


class Scheduler(object):
    def __init__(self, task_model):
        self.tasks = task_model.get_tasks()
        logger.info(
            [("%d:%s") % (task['duration'],task['url']) for task in self.tasks]
        )

    def start(self):
        """ Runs our scheduler."""
        logger.info('running')
        while True:
            print 'running'
        

if __name__ == "__main__":
    Scheduler(TaskModel).start()
