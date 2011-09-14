from __future__ import with_statement

import gevent
import time

from constants import TRACKER_THREAD_TIMEOUT

class Tracker:

    tracker_id = None
    interval = None
    source = None
    last_modified = None

    def __init__(self, tracker_id):
        self.tracker_id = tracker_id

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

    def grab_data(self):
        try:
            with gevent.Timeout(TRACKER_THREAD_TIMEOUT):
                # Do something
                x = 0
                for i in xrange(0, self.source):
                    x = x + i
                    gevent.sleep(0)
                print time.strftime('%H:%M:%S'), 'Tracker ID:', self.tracker_id
        except gevent.Timeout, timeout:
            print time.strftime('%H:%M:%S'), 'Tracker ID:', self.tracker_id, 'Timeout.'
        data = {'time': time.time(),
                'value': randoint(1,1000)}
        self.storage.put(self, data)
