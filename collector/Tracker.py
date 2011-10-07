"""This module contains Tracker class wich is responsible for gathering raw data
from datasource and return parsed values.
"""

import time

from datasources import get_data_source
from datasources.Errors import BaseGrabError, UnknownDatasourceError

RESPONSE_URL_ERROR = 50001
RESPONSE_GEVENT_TIMEOUT = 50504

class Tracker(object):

    """Gather data from datasource and parse them using appropriate parser.

    :Instance variables:
        - `tracker_id`: unique ID of tracker.
        - `interval`: interval to grab data.
        - `source`: string which contains target for this tracker.
        - `source_type`: string which contains type of the raw data (XML, HTML,
          JSON etc.)
        - `last_modified`: time (in seconds) of last modification.
        - `values_to_get`: a list of XPATH or other queries for parser.
        - `values`: a list of parsed values.
    """

    tracker_id = None
    interval = None
    last_modified = None
    source_type = None # JSON, XML, etc.
    source = None
    values = None


    def __init__(self, tracker_id, source, source_type, values_to_get,
                 interval, storage):
        """Initialize the tracker with valid configuration.
        """
        self.tracker_id = tracker_id
        self.source = source
        self.source_type = source_type
        self.values_to_get = values_to_get
        self.interval = interval
        self.storage = storage

        self.values = []
        self.last_modified = 0
        interval = 0

    def get_id(self):
        return self.tracker_id

    def _grab_data():
        """Grab data from datasource.
        """
        ds = get_data_source(self.source)
        self._raw_data = ds._grab_data()

    def _parse_data(self):
        """Parse raw data with appropriate parser and save gathered values in
        `values` attribute.
        """
        # TODO: create a parser instance appropriate to the `self.source_type`.
        parser = None
        parser.initialize()
        parser.parse()
        parser.xpath()

    def _check_data(self):
        """Check if the data stored in `values` attribute has the same type as
        it was requested by the user.
        """
        # Currecntly we cannot implement this method correctly.
        pass

    def _save_data(self):
        """Save data to storage.
        """
        # TODO: store data to the storage.
        pass
        
    def _process_datasource_exception(e):
        # TODO: process exception here
        pass

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
            self.last_modified = time.time()
        except BaseGrabError, e:
            self._process_datasource_exception(e)

