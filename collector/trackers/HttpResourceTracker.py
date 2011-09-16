from __future__ import with_statement

from gevent import monkey
monkey.patch_socket()

from abc import ABCMeta, abstractmethod
from . import BaseTracker

import gevent
import urllib2
import random
import time

from settings import TRACKER_THREAD_TIMEOUT
from config import logger
from trackers.constants import RESPONSE_URL_ERROR, RESPONSE_GEVENT_TIMEOUT

class HttpResourceTracker(BaseTracker):
    """
    This class should be used by all trackers, based on Http Resources.
    It has abstract method `parse_data`, which parses html response data using 
    corresponding parser.
    """

    @abstractmethod
    def parse_data(self, data, html): pass
    
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
        
        if data.get('size'):
            self.parse_data(data, html)
        
        self.storage.put(self, data)
