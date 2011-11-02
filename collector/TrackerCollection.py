import gevent

from config.collector import trackers_refresh_interval
from shared.services.services_api import trackers_api
from shared.trackers import Tracker


class TrackerCollection:

    trackers = None
    scheduler = None

    def __init__(self, scheduler, storage=None):
        self.scheduler = scheduler
        self.storage = storage
        self.trackers = {}

        self._trackers_api = None

    def _tracker_updater(self):
        while True:
            if not self.trackers:
                # This is the first iteration and we need all trackers.
                update_interval = None
            else:
                # TODO: move this to configuration.
                update_interval = None #5 due to some problems we should use non by now

            updated_trackers = \
               self._trackers_api.get_trackers(modified_since=update_interval)

            for tracker in updated_trackers:
                tracker.storage = self.storage
                track_id = tracker.get_id()
                if track_id in self.trackers:
                    del self.trackers[track_id]
                    self.scheduler.remove_tracker(track_id)

                self.trackers[track_id] = tracker
                self.scheduler.add_tracker(tracker)

            gevent.sleep(trackers_refresh_interval)

    def _initialize(self):
        """Perform all required initialization.
        """
        self._trackers_api = trackers_api()

    def start(self):
        self._initialize()
        gevent.spawn(self._tracker_updater)

