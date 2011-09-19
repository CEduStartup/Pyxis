from abc import ABCMeta, abstractmethod

class BaseTracker:
    __metaclass__ = ABCMeta
    
    tracker_id = None
    interval = None
    source = None
    last_modified = None
    source_type = None # JSON, XML, etc.
    values = [
        ('body.div[0]', 'int')
    ]

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

    @abstractmethod
    def grab_data(): pass


from HttpResourceTracker import HttpResourceTracker
from XmlResourceTracker import XmlResourceTracker