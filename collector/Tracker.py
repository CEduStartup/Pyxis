from __future__ import with_statement

import gevent
from gevent import monkey
monkey.patch_socket()

import urllib2

import random
import time

from settings import TRACKER_THREAD_TIMEOUT
from config import logger

class Tracker:

    tracker_id = None
    interval = None
    source = None
    last_modified = None

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

    def grab_data(self):
        html = ''
        try:
            with gevent.Timeout(TRACKER_THREAD_TIMEOUT):
                response = urllib2.urlopen(self.source)
                html = response.read()
        except gevent.Timeout, timeout:
            logger.warn('URL read timeout - %s' % self.source)
        data = {'time': time.time(),
                'value': html}
        self.storage.put(self, data)

if __name__ == '__main__':
    logger.info('main')

    class DummyStorage:
        def put(self, tracker, data):
            logger.info('put - tracker: %s (%s), time: %s, data length=%d' % (
                        tracker.get_id(), tracker.get_source(), data['time'], len(data['value'])))

    storage = DummyStorage()

    greenlets = []
    for idx, url in enumerate(['http://google.com', 'http://msn.com', 'http://facebook.com',
                               'http://developers.org.ua', 'http://habrahabr.ru']):
        tracker = Tracker('tracker_%d' % idx, storage)
        tracker.set_source(url)
        greenlets.append(gevent.spawn(tracker.grab_data))
    logger.info('doing')
    gevent.joinall(greenlets)
