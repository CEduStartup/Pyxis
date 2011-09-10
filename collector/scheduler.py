from config import logger
from mocks import TaskModel
from workers import Worker

from collections import deque

import time

class Task(dict):
    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self['ttl'] = 0
    
    def __str__(self):
        return "%d: %s" % (self['duration'], self['url'])

class Scheduler(object):
    def __init__(self, task_model):
        self.tasks = [Task(task) for task in task_model.get_tasks()]
        logger.info(
            [str(task) for task in self.tasks]
        )

    def start(self):
        """ Runs our scheduler."""
        logger.info('running')
        upcoming_tasks = deque(sorted([task for task in self.tasks],
                                      key=lambda t: t['ttl']))
        
        while True:
            task = upcoming_tasks.popleft()
            if task['ttl']:
                time.sleep(task['ttl'])
                for t in upcoming_tasks:
                    t['ttl'] = t['ttl'] - task['ttl'] if task['ttl'] <= t['ttl'] else 0
            self.get_worker().process_task(task)
            task['ttl'] = task['duration']
            upcoming_tasks.append(task)

            
    def get_worker(self):
        return Worker()
        

if __name__ == "__main__":
    Scheduler(TaskModel).start()
