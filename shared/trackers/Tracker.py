# Trackers representation classes.
# Each tracker has a datasource, which knows where to get data from and how to
# get them.
import abc


class TrackerBase:
    """Base class for trackers."""
    tracker_id = None
    interval = None
    source = None
    last_modified = None
    source_type = None # JSON, XML, etc.

    def __init__(self, tracker_id, storage):
        self.tracker_id = tracker_id
        self.storage = storage

    def get_id(self):
        return self.tracker_id

    def get_interval(self):
        return self.interval

    def get_source(self):
        return self.source

    def get_last_modified(self):
        return self.last_modified

    def set_interval(self, interval):
        self.interval = interval

    def set_source(self, source):
        self.source = source

    def set_last_modified(self, last_modified):
        self.last_modified = last_modified

    @abc.abstractmethod
    def grab_data(): pass


class Tracker(TrackerBase):
    pass


class DummyTracker(Tracker):
    def grab_data():
        from config import logger
        logger.info('just simple message from tracker %s' % self.get_id())
