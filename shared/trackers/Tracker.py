"""This module contains Tracker class wich is responsible for gathering raw data
from datasource and return parsed values.
"""

import time
import traceback

from config.init.trackers import sender
from shared.trackers.datasources.factory import get_datasource
from shared.trackers.datasources.Errors import UnknownDatasourceError, \
                                               BaseGrabError
from shared.Parser import get_parser, ParserError


class Tracker(object):

    """Gather data from datasource and parse them using appropriate parser.

    :Instance variables:
        - `tracker_id`: unique ID of tracker.
        - `refresh_interval`: interval to grab data.
        - `_datasource_settings`: JSON obkect which
        - `last_modified`: time (in seconds) of last modification.
        - `values_to_get`: a list of XPATH or other queries for parser.
        - `values`: a list of parsed values.
    """


    def __init__(self, tracker_id, refresh_interval, datasource_settings,
                 tracker_name=None):
        """Initialize the tracker with valid configuration.

        :Parameters:

            - `tracker_id`: `int`. Unique ID of the tracker.
            - `refresh_interval`: `int`. How often (in seconds) we need
                                   to refresh data.
            - `datasource_settings`: `dict` (or list of dicts in case when
                                     tracker uses multiple datasources) of the
                                     following structure: ::

                {
                  `access_method`: `int`. Describes protocol which should be
                                          used to grab data (HTTP, XMLRPC,
                                          SOAP, etc.)
                  `query`: JSON encoded object. Required fields:
                           - `URI`: `str`. URI of the resource.
                           - `method_name`: `str`. In case of XMLRPC or SOAP
                             this field contains the name of the method which
                             should be called to grab data.
                           - `params`: `dict` pairs of parameter name and
                             parameter value to pass them to `method_name
                  `datatype`: `str`. Type of the data e.i. HTML, XML, CSV,
                              JSON, etc.
                  `values`: `list` of `dict` of the following structure: ::

                              {
                                `value_id`: `int` unique ID of the value.
                                `type`: `str`. A rule to validate value.
                                        Currently `int` or `float`.
                                `extraction_rule`: `str`. XPATH, JSONPATH,
                                                   regexp, etc.
                              }
                }

        """
        self.tracker_id = tracker_id
        self.name = tracker_name
        self.refresh_interval = refresh_interval
        self._datasource_settings = datasource_settings

        self.last_modified = 0

        self._datasources = None
        self._parsers = None
        self._raw_data = None
        self._clean_data = None

    def get_id(self):
        """Return a string with unique tracker ID.
        """
        return self.tracker_id

    def touch(self, timestamp=None):
        """Update last modified attribute.

        :Parameters:
            - `timestamp`: float. If it's present then last modified attribute
              will be set to its value, otherwise current time will be used.

        :Return:
            - new value of `last_modified` attribute.
        """
        self.last_modified = timestamp or time.time()
        return self.last_modified

    def _create_datasources(self):
        """Create datasource (or datasources) using `_datasource_settings`
        atribute. In case when it's a `dict` then current tracker use only 1
        datasource. In case of list we need to create more datasources.
        """
        def create_datasource(settings_dict):
            """Create datasource instance. Please see description of
            `datasource_settings` (of `__init__()` method) to see a format of
            `settings_dict`.

            :Return:
                - datasource instance.

            """
            try:
                datasource = get_datasource(settings_dict)
                print datasource
            except UnknownDatasourceError, err:
                # TODO: handle this error correctly.
                print 'SOME ERROR', err
            return datasource

        if isinstance(self._datasource_settings, dict):
            self._datasources = [create_datasource(self._datasource_settings),]
        else:
            self._datasources = [create_datasource(setting) for setting in
                                 self._datasource_settings]

        return len(self._datasources)

    def _grab_data(self):
        """Grab data from datasource.
        """
        self._create_datasources()

        for datasource in self._datasources:
            try:
                datasource.grab_data()
            except BaseGrabError:
                # Log this event.
                print 'GRAB ERROR'
                pass

    def _parse_data(self):
        """Parse raw data with appropriate parser and save gathered values in
        `values` attribute.
        """
        self._parsers = []
        for datasource in self._datasources:
            try:
                parser = get_parser(datasource.datatype)
                parser.initialize()
                parser.parse(datasource.get_raw_data())
                self._parsers.append(parser)
            except ParserError:
                # TODO: we need to log this error and notify another components
                # about it.
                print 'PARSER ERROR'

        self._clean_data = [self._parsers.xpath(query)
                            for query in self.queries]

    def _check_data(self):
        """Check if the data stored in `values` attribute has the same type as
        it was requested by the user.
        """
        # Currecntly we cannot implement this method correctly.
        # TODO: validate self._clean_data
        pass

    def _save_data(self):
        """Save data to storage.
        """
        # TODO: store data to the storage.
        pass

    def _process_datasource_exception(self, err):
        # TODO: process exception here
        print 'ERROR', err
        sender.fire('LOGGER.DEBUG',
                    message='DATASOURCE EXCEPTION %s' % (type(err),))

    def process(self):
        """Main logic of the tracker.
        Create appropriate datasource, and get raw data. Then parse the data
        using appropriate parser and try to validate them. The last step is to
        save parsed values to the storage.
        """
        try:
            self._grab_data()
            self._parse_data()
            self._check_data()
            self._save_data()
        except BaseGrabError, err:
            self._process_datasource_exception(err)
        except Exception:
            sender.fire('LOGGER.CRITICAL', message=traceback.format_exc())
        finally:
            self.last_modified = time.time()

    def __repr__(self):
        return '<Tracker %s: `%s` %s>' % (self.tracker_id, self.name,
                                          self._datasource_settings)
    def get_values(self):
        if isinstance(self._datasource_settings, dict):
            ds = [self._datasource_settings,]
        else:
            ds = self._datasource_settings

        values = {}
        for d in ds:
            for v in d['values']:
                values[v['value_id']] = v
        return values

