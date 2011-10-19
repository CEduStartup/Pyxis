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

from config.collector import tracker_thread_timeout
from config.init.trackers import sender

class DatasourceHTTP(DatasourceCommon):

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
        print config
        parsed_settings = json.loads(config['query'])
        self._target = parsed_settings['URI']
        # TODO: We definitely need more initialization here.

    def grab_data(self):
        start_time = time.time()
        try:
            with gevent.Timeout(tracker_thread_timeout):
                request = urllib2.Request(self._target)
                response = urllib2.urlopen(request)
                self.raw_data = response.read()
                self.response_code = response.code
        except urllib2.HTTPError, err:
            self.response_code = err.code
            sender.fire('LOGGER.WARNING', message='HTTPError for %s: %d' %
                                                  (self.source, err.code))
            raise ResponseHTTPError(err)
        except urllib2.URLError, err:
            sender.fire('LOGGER.WARNING', message='URLError for %s: %s' %
                                                  (self.source, err.reason))
            raise ResponseURLError(err)
        except gevent.Timeout, err:
            sender.fire('LOGGER.WARNING', message='URL Gevent timeout - %s'
                                                  % self.source)
            raise ResponseGeventTimeout()

        now = time.time()
        self.grab_spent_time = now-start_time
        return self.raw_data

