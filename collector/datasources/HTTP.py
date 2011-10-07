"""This module contains a base class for all datasources which use HTTP
protocol to grab data.
"""

from __future__ import with_statement

from gevent import monkey; monkey.patch_socket()
from .Common import DatasourceCommon
from .Errors import ResponseHTTPError, ResponseURLError, ResponseGeventTimeout

import gevent
import urllib2
import time

from trackers.constants import RESPONSE_URL_ERROR, RESPONSE_GEVENT_TIMEOUT
from config.collector import tracker_thread_timeout

class DatasourceHTTP(DatasourceCommon):
    def initialize(self):
        pass
        
    def grab_data(self):
        start_time = time.time()
        try:
            with gevent.Timeout(tracker_thread_timeout):
                request = urllib2.Request(self._target)
                response = urllib2.urlopen(request)
                self.raw_data = response.read()
                self.response_code = response.code
        except urllib2.HTTPError, e:
            self.response_code = e.code
            raise ResponseHTTPError(e)
            #logger.warn('HTTPError for %s: %d' % (self.source, e.code))
        except urllib2.URLError, e:
            raise ResponseURLError(e)
            #self.response_code = RESPONSE_URL_ERROR
            #logger.warn('URLError for %s: %s' % (self.source, e.reason))
        except gevent.Timeout, e:
            #logger.warn('URL Gevent timeout - %s' % self.source)
            #self.response_code = RESPONSE_GEVENT_TIMEOUT
            raise ResponseGeventTimeout()
            
        now = time.time()
        self.grab_spent_time = now-start_time
        return self.raw_data

