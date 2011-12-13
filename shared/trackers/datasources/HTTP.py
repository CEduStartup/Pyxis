"""This module contains a base class for all datasources which use HTTP
protocol to grab data.
"""

from __future__ import with_statement
import gevent
import json
import time
import urllib2

from .Common import DatasourceCommon
from .Errors import ResponseHTTPError, ResponseURLError, \
                    ResponseGeventTimeout
from shared.events.Event import LoggerWarningEvent, LoggerDebugEvent
from shared.trackers.datasources.query_parsers import JSON
from .query_parsers.JSON import QueryParserJSON

from config.collector import tracker_thread_timeout
from config.init.trackers import sender

class DatasourceHTTP(DatasourceCommon, QueryParserJSON):

    """This datasource type is responsible for grabbing data via HTTP
    protocol.
    """

    def __init__(self, settings):
        """Class constructor.

        :Parametrs:
            - `settings`: `dict` which must contains following keys:
                - `access_method`: `str`. Describes how to access to the data
                  i.e.: HTTP, SOAP, XMLRPC, etc.
                - `query`: JSON object. In case of HTTP `access_method` must
                  contains `URI` attribute with http address of raw data.
                - `datatype`: format of raw data i.e. html, csv, xml, etc.
        """
        DatasourceCommon.__init__(self, settings)

        self._target = None
        self.response_code = None
        self.initialize(settings)

    def initialize(self, config):
        """Initialize datasource with the given configuration.

        :Parameters:
            - `config`: dictionary of the same format as a `settings` dict
              described in `__init__()`.
        """
        query = self.parse_query(config['query'])
        self._target = query['URI']

    def grab_data(self):
        self.request_time = time.time()
        try:
            with gevent.Timeout(tracker_thread_timeout):
                request = urllib2.Request(self._target)
                request.add_header('User-agent', 'Mozilla/5.0')
                response = urllib2.urlopen(request)
                self.raw_data = response.read()
                self.response_code = response.code
        #TODO: Fire corresponding tracker and/or datasource events here
        #instead of general logger events.
        except urllib2.HTTPError, err:
            self.response_code = err.code
            sender.fire(LoggerWarningEvent, message='HTTPError for %s: %d' %
                                                  (self._target, err.code))
            raise ResponseHTTPError(err)
        except urllib2.URLError, err:
            sender.fire(LoggerWarningEvent, message='URLError for %s: %s' %
                                                  (self._target, err.reason))
            raise ResponseURLError(err.reason)
        except gevent.Timeout, err:
            sender.fire(LoggerWarningEvent, message='URL Gevent timeout - %s'
                                                  % self._target)
            raise ResponseGeventTimeout()

        now = time.time()
        self.grab_spent_time = now - self.request_time
        sender.fire(LoggerDebugEvent, message='Processed "%s" with [%d] in %.2fsecs"' % (
            self._target, self.response_code, self.grab_spent_time))

    def get_raw_data(self):
        return self.raw_data
