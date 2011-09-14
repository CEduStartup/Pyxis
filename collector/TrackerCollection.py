from __future__ import with_statement

import gevent

from Tracker import Tracker
from settings import TRACKERS_REFRESH_INTERVAL

class TrackerCollection:

    trackers = None
    scheduler = None

    def __init__(self, scheduler, storage=None):
        self.scheduler = scheduler
        self.storage = storage
        self.trackers = {}

    def trackerUpdater(self):
        with open('trackers.pyxis', 'r') as fl:
            old_trackers = set(self.trackers.keys())
            for line in fl:
                key, interval, source = map(int, line.split())
                if key in old_trackers:
                    self.trackers[key].set_interval(interval)
                    self.trackers[key].set_source(source)
                    old_trackers.remove(key)
                else:
                    self.trackers[key] = Tracker(key, storage=self.storage)
                    self.trackers[key].set_interval(interval)
                    self.trackers[key].set_source(source)
                    self.scheduler.add_tracker(self.trackers[key])
            for tracker in old_trackers:
                self.scheduler.remove_tracker(tracker)
        gevent.sleep(TRACKERS_REFRESH_INTERVAL)
