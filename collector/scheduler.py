##
## Pseudo-code prototype for scheduler, very primitive version.
##
from __future__ import with_statement
import sys
import gevent
from gevent import socket
from gevent.pool import Pool
import time


PARALLEL_THREADS_NUM = 10
GET_DATA_TIMEOUT = 1


class Tracker:
    """Tracker object.

    Knows hot to get data for itself.
    """

    def __init__(self):
        self.last_get = None
        self.last_status = None

    def get_data(self):
        ...
        return result


class TrackersCollection:
    """Trackers collection.

    Keeps information about all configured trackers.
    """
    self.trackers = {}
    self.db = mongodb

    def reload(self):
        trackers_config = self.db.load_trackers()
        for tracker_config in trackers_config:
            self.trackers[tracker.id] = self._trackerFactory(tracker_config))

    def get_trackers(self):
        return self.trackers


class Scheduler:
    """Scheduler.

    Runs everything.
    """
    def __init__(self, trackers_collection):
        self.trackers_collection = trackers_collection
        self.pool = Pool(PARALLEL_THREADS_NUM)
        self.results = {}

    def run(self):
        self._main_loop()

    def _main_loop(self):
        while(True):
            for tracker_id in self.trackersCollection.get_trackers():
                if self._time_to_run(tracker):
                    self.pool.spawn(self._get_tracker_data, tracker)
            self.pool.join()

    def _get_tracker_data(self, tracker):
        result = tracker.get_data()
        tracker.db.save(tracker, result)
        results[tracker.tracker_id] = {'status': STATUS,
                                       'last_get': time.time()}

    def _time_to_run(self, tracker):
        data = self.results.get(tracker.tracker_id)
        return (not data or data['last_get'] == None or \
                time.time() - data['last_get'] > tracker.interval)


if __name__ == 'main':
    trackers_collection = TrackersCollection()
    trackers_collection.reload()
    scheduler = Scheduler(trackers_collection)
    scheduler.run()
