from __future__ import with_statement

import gevent
from gevent import monkey
monkey.patch_socket()

import urllib2


import random
import time

from settings import TRACKER_THREAD_TIMEOUT
from config import logger

JSON_TRACKER = 'json'
XML_TRACKER  = 'xml'

RESPONSE_URL_ERROR = 50001
RESPONSE_GEVENT_TIMEOUT = 50504

class Tracker:

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

    def grab_data(self):
        """ Takes data from resorce, parses it and put to storage. 
            
            HTTP and URL errors, as well as Gevent's are handled too
        """
        data = dict(value=None)
        start_time = time.time()
        try:
            with gevent.Timeout(TRACKER_THREAD_TIMEOUT):
                request = urllib2.Request(self.source)
                response = urllib2.urlopen(request)
                html = response.read()
                data.update(dict(code=response.code,
                                 size=len(html)))
        except urllib2.HTTPError, e:
            data['code'] = e.code
            logger.warn('HTTPError for %s: %d' % (self.source, e.code))
        except urllib2.URLError, e:
            data['code'] = RESPONSE_URL_ERROR
            logger.warn('URLError for %s: %s' % (self.source, e.reason))
        except gevent.Timeout, e:
            data['code'] = RESPONSE_GEVENT_TIMEOUT
            logger.warn('URL Gevent timeout - %s' % self.source)
            
        now = time.time()
        data.update(dict(time=now, process_time=now-start_time))
        
        self.storage.put(self, data)
        

