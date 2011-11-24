"""This module contains implementation of scheduler.
"""

import gevent
import gevent.coros
import config.collector as config
import time

from gevent.pool import Pool
from gevent.queue import PriorityQueue, Queue


def _get_int_time(t_stamp=None):
    """Helper function.
    Return an integer value of `t_stamp`. In case when `t_stamp` is None return current
    time.
    """
    return int(t_stamp or time.time())


class Scheduler(object):

    """This is a scheduler class.
    """

    # Thread pool.
    pool = None

    # All currently active tasks.
    tasks = None

    # Tasks that already scheduled and will be executed as soon as free pool
    # slot appear.
    to_run = None

    # All trackers that our system processing.
    _trackers = None
    _trackers_lock = None

    def __init__(self):
        self.tasks = PriorityQueue()
        self.to_run = Queue()
        self.pool = Pool(config.parallel_threads_num)
        self._trackers = {}
        self._trackers_lock = gevent.coros.RLock()

    def _run_tasks(self):
        """The main purpose of this method is to take tasks from to_run and
        spawn threads for them. This functionality moved to separate thread
        because spawn method is blocking. This way it would not block
        processing of upcoming tasks.
        """
        while True:
            tracker = self.to_run.get()
            self.pool.spawn(tracker.process)

    def _schedule_tasks(self):
        """This method is processing upcoming tasks, deletes them if necessary
        and schedules them.
        """
        while True:
            run_time, tracker = self.tasks.get()

            # This tracker was marked for deletion, so we just pop it from
            # queue.
            if tracker.is_deleted():
                continue

            cur_time = _get_int_time()
            if cur_time < run_time:
                self.tasks.put((run_time, tracker))
                gevent.sleep(
                   min(time.time()-cur_time, config.scheduler_maximum_sleep))
                continue
            self.to_run.put(tracker)
            self.tasks.put((run_time + tracker.refresh_interval, tracker))

    def get_run_queue_size(self):
        """Return a size of run queue.
        """
        return self.to_run.qsize()

    def add_tracker(self, tracker):
        """Add tracker to scheduler.
        You can use this method to update tracker configuration.

        If the tracker with such id is already present than its configuration
        will be updated (and tracker will be rescheduled if `refresh_interval`
        changed).
        """
        t_id = tracker.tracker_id

        # Check if such tracker is already in scheduler.
        if t_id in self._trackers:
            curr_tracker =  self._trackers[t_id]

            # Tracker is present but refresh_interval is changed, so we need to
            # delete tracker from scheduler and reschedule it.
            if (tracker.refresh_interval != curr_tracker.refresh_interval):
                self.remove_tracker(tracker.tracker_id)

            # `refresh_interval` is not changed so we can update configuration
            # without rescheduling.
            else:
                curr_tracker.update_settings(tracker)
                return

        # Modification of _trackers dict is an atomic operation so we need to
        # get exclusive access.
        self._trackers_lock.acquire()
        try:
            self._trackers[tracker.tracker_id] = tracker
            self.tasks.put((_get_int_time(), tracker))
        finally:
            self._trackers_lock.release()

    def remove_tracker(self, tracker_id):
        """Remove tracker from scheduler.
        """
        # Modification of _trackers dict is an atomic operation so we need to
        # get exclusive access.
        self._trackers_lock.acquire()
        try:
            self._trackers[tracker_id].set_deleted()
            del self._trackers[tracker_id]
        finally:
            self._trackers_lock.release()

    def start(self):
        gevent.spawn(self._run_tasks)
        gevent.spawn(self._schedule_tasks)

