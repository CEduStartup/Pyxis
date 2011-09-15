import gevent
import time

from settings import PARALLEL_THREADS_NUM, TRACKERS_REFRESH_INTERVAL

from gevent.pool import Pool
from gevent.queue import PriorityQueue, Queue

class Scheduler:

    # Thread pool.
    pool = None
    # All currently active tasks.
    tasks = None
    # Tasks that already scheduled and will be executed as soon as free pool
    # slot appear.
    to_run = None
    # Tasks that would be deleted as soon as it will be tried to schedule.
    to_remove = None

    def __init__(self):
        self.tasks = PriorityQueue()
        self.to_run = Queue()
        self.to_remove = set()
        self.pool = Pool(PARALLEL_THREADS_NUM)

    def _get_current_time(self):
        return int(time.time())

    def _run_tasks(self):
        """The main purpose of this method is to take tasks from to_run and spawn
        threads for them. This functionality moved to separate thread because
        spawn method is blocking. This way it would not block processing of
        upcoming tasks.
        """
        while True:
            tracker = self.to_run.get()
            self.pool.spawn(tracker.grab_data)

    def _schedule_tasks(self):
        """This method is processing upcoming tasks, deletes them if necessary
        and schedules them.
        """
        while True:
            time, tracker = self.tasks.get()
            if tracker.get_id() in self.to_remove:
                self.to_remove.remove(tracker.get_id())
                continue
            cur_time = self._get_current_time()
            if cur_time < time:
                self.tasks.put((time, tracker))
                gevent.sleep(min(time - cur_time, TRACKERS_REFRESH_INTERVAL))
                continue
            self.to_run.put(tracker)
            self.tasks.put((time + tracker.get_interval(), tracker))

    def get_run_queue_size(self):
        return self.to_run.qsize()

    def add_tracker(self, tracker):
        self.tasks.put((self._get_current_time(), tracker))

    def remove_tracker(self, tracker):
        self.to_remove.add(tracker)

    def start(self):
        gevent.spawn(self._run_tasks)
        gevent.spawn(self._schedule_tasks)

