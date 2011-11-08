import gevent
import time

from config.collector import trackers_refresh_interval
from shared.services.services_api import trackers_api


# Time delta in seconds for trackers update.
# TODO: Check whether 5 sec is enough.
_UPDATE_DELTA = 5


class TrackerCollection:

    trackers = None
    scheduler = None

    def __init__(self, scheduler, storage=None):
        self.scheduler = scheduler
        self.storage = storage
        self.trackers = {}

        self._trackers_api = None

    def _tracker_updater(self):
        """Manage trackers queue.
        Add new trackers and update trackers configuration in case when it
        changed.
        """
        while True:
            if not self.trackers:
                # This is the first iteration and we need all trackers.
                modified_since = None
            else:
                modified_since = (time.time() - trackers_refresh_interval -
                                  _UPDATE_DELTA)

            updated_trackers = \
               self._trackers_api.get_trackers(modified_since=modified_since)

            for tracker in updated_trackers:
                tracker.storage = self.storage
                track_id = tracker.get_id()

                if track_id in self.trackers:
                    # Refresh interval was changed and we need to reschedule
                    # this tracker.
                    if (self.trackers[track_id].refresh_interval !=
                        tracker.refresh_interval):

                        del self.trackers[track_id]
                        self.scheduler.remove_tracker(track_id)

                        self.trackers[track_id] = tracker
                        self.scheduler.add_tracker(tracker)

                    # Refresh interval is the same, so we only need to update
                    # configuration without rescheduling.
                    else:
                        curr_tracker = self.trackers[track_id]
                        curr_tracker.datasource_settings = \
                           tracker.datasource_settings
                        curr_tracker.name = tracker.name

                else:
                    self.trackers[track_id] = tracker
                    self.scheduler.add_tracker(tracker)

            gevent.sleep(trackers_refresh_interval)

    def _initialize(self):
        """Perform all required initialization.
        """
        self._trackers_api = trackers_api()

    def start(self):
        """Start main method in separate greenlet.
        """
        self._initialize()
        gevent.spawn(self._tracker_updater)

