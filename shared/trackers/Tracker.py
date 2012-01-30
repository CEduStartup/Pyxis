"""This module contains Tracker class wich is responsible for gathering raw data
from datasource and return parsed values.
"""

import time
import traceback

from config.init.trackers import sender
from shared.events.Event import TrackerGrabSuccessEvent, TrackerGrabFailureEvent, \
                                LoggerCriticalEvent, LoggerDebugEvent
from shared.trackers import VALUE_TYPES
from shared.trackers.datasources.factory import get_datasource
from shared.trackers.datasources.Errors import BaseGrabError
from shared.trackers.value_extractor import ValueExtractor
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
        - `_deleted`: bool. `True` if tracker marked for deletion otherwise
          `False`
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
                  `data_type`: `str`. Type of the data e.i. HTML, XML, CSV,
                              JSON, etc.
                  `values`: `list` of `dict` of the following structure: ::

                              {
                                `value_id`: `int` unique ID of the value.
                                `type`: `int`. A rule to validate value.
                                `extraction_rule`: `str`. XPATH, JSONPATH,
                                                   regexp, etc.
                              }
                }

        """
        self.tracker_id = tracker_id
        self.name = tracker_name
        self.refresh_interval = refresh_interval
        self.datasource_settings = datasource_settings
        self.storage = None

        self.last_modified = 0

        self._datasources = None
        self._parsers = None
        self._raw_data = None
        self._clean_data = None
        self._deleted = False
        self._value_extractor = ValueExtractor()


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
            datasource = get_datasource(settings_dict)
            return datasource

        if isinstance(self.datasource_settings, dict):
            self._datasources = [(create_datasource(self.datasource_settings),
                                  self.datasource_settings)]
        else:
            self._datasources = [(create_datasource(settings),
                                  settings) for settings in
                                 self.datasource_settings]

        return len(self._datasources)

    def _grab_data(self):
        """Grab data from datasource.
        """
        self._create_datasources()

        for datasource in map(lambda x: x[0], self._datasources):
            datasource.grab_data()
            sender.fire(TrackerGrabSuccessEvent, tracker_id=self.tracker_id)

    def set_deleted(self):
        """Mark tracker as `deleted`, so scheduler will not process it.
        """
        self._deleted = True

    def is_deleted(self):
        """Return `True` if the tracker was marked for deletion, ptherwise
        return `False`.
        """
        return self._deleted

    def _parse_data(self):
        """Parse raw data with appropriate parser and save gathered values in
        `values` attribute.
        """
        self._parsers = []
        self._clean_data = {}
        for (datasource, settings) in self._datasources:
            try:
                parser = get_parser(settings['data_type'])
                parser.initialize()
                parser.parse(datasource.get_raw_data())
                self._parsers.append(parser)

                for extract_value in settings['values']:
                    xpath_result = \
                       parser.get_value(extract_value['extraction_rule'])
                    value = None
                    if isinstance(xpath_result, list) and len(xpath_result) > 0:
                        if isinstance(xpath_result[0], str):
                            value = xpath_result[0]
                        else:
                            value = xpath_result[0].text

                    if not value is None:
                        clean_value = \
                            self._value_extractor.extract_number(value,
                                VALUE_TYPES[extract_value['type']]['name'])
                        self._clean_data[extract_value['value_id']] = clean_value

            except ParserError, e:
                # TODO: we need to log this error and notify another components
                # about it.
                sender.fire(LoggerCriticalEvent, message=
                            'Parsing error for tracker %s' % self.tracker_id)
                raise

    def _extract_value(self, value, value_type):
        """Here we cast numercial value from what we extracted from document
        grabbed.

        Example:
            - grabbed: "10$", after cast it's: 10.
            - grabbed: "10,000,000", after cast it's: 10000000.
        """
        clean_value = self._value_extractor.extract_number(value, value_type)
        return clean_value

    def _validate_data(self):
        """Check if the data stored in `values` attribute has the same type as
        it was requested by the user.
        """
        # Currently we cannot implement this method correctly.
        # TODO: validate self._clean_data
        pass

    def _save_data(self):
        """Save data to storage.
        """
        sender.fire(LoggerDebugEvent, message='Save data: %s %s' %
                                    (self.tracker_id, self._clean_data))
        # Currently we process only first datasource.
        self.storage.put(self,
                         {'timestamp': self._datasources[0][0].request_time,
                          'data':      self._clean_data})

    def _process_datasource_exception(self, err):
        """Process grab errors.

        :Parameters:
            - `err`: an instance of execption.
        """
        sender.fire(TrackerGrabFailureEvent, tracker_id=self.tracker_id,
                    error_details='** TO BE DONE **')#str(err.reason))

    def process(self):
        """Main logic of the tracker.
        Create appropriate datasource, and get raw data. Then parse the data
        using appropriate parser and try to validate them. The last step is to
        save parsed values to the storage.
        """
        try:
            self._grab_data()
            self._parse_data()
            self._validate_data()
            self._save_data()
        except BaseGrabError, err:
            self._process_datasource_exception(err)
        except Exception, err:
            sender.fire(LoggerCriticalEvent, message=traceback.format_exc())
        finally:
            self.last_modified = time.time()

    def set_storage(self, storage):
        """ Attaches storages to current tracker. """
        self.storage = storage

    def __repr__(self):
        return '<Tracker %s: `%s` `refresh_interval`: %s %s>' % \
           (self.tracker_id, self.name, self.refresh_interval,
            self.datasource_settings)

    def get_values(self):
        if isinstance(self.datasource_settings, dict):
            ds = [self.datasource_settings,]
        else:
            ds = self.datasource_settings

        values = {}
        for d in ds:
            for v in d['values']:
                values[v['value_id']] = v
        return values

    def update_settings(self, tracker_obj):
        """Update tracker configuration from another tracker object.
        """
        self.name = tracker_obj.name
        self.refresh_interval = tracker_obj.refresh_interval
        self.datasource_settings = tracker_obj.datasource_settings

