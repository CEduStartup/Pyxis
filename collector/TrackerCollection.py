from __future__ import with_statement

import gevent

from trackers import Tracker
from config.collector import trackers_refresh_interval

class TrackerCollection:

    trackers = None
    scheduler = None

    def __init__(self, scheduler, storage=None):
        self.scheduler = scheduler
        self.storage = storage
        self.trackers = {}

    def _tracker_updater(self):
        while True:
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
            gevent.sleep(trackers_refresh_interval)

    def start(self):
        gevent.spawn(self._tracker_updater)

