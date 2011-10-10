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

from shared.trackers.constants import RESPONSE_URL_ERROR, RESPONSE_GEVENT_TIMEOUT
from config.collector import tracker_thread_timeout
from config.init.trackers import sender

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
            sender.fire('LOGGER.WARNING', message='HTTPError for %s: %d' % (self.source, e.code))
            raise ResponseHTTPError(e)
        except urllib2.URLError, e:
            sender.fire('LOGGER.WARNING', message='URLError for %s: %s' % (self.source, e.reason))
            raise ResponseURLError(e)
        except gevent.Timeout, e:
            sender.fire('LOGGER.WARNING', message='URL Gevent timeout - %s' % self.source)
            raise ResponseGeventTimeout()
            
        now = time.time()
        self.grab_spent_time = now-start_time
        return self.raw_data

