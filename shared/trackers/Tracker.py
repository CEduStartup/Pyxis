"""This module contains Tracker class wich is responsible for gathering raw data
from datasource and return parsed values.
"""

import time
import traceback

from EventSender import sender
from shared.Parser import get_parser


from datasources import get_data_source
from datasources.Errors import BaseGrabError, UnknownDatasourceError
from shared.Parser import get_parser

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
    queries = None


    def __init__(self, tracker_id, source, source_type, queries,
                 interval, storage):
        """Initialize the tracker with valid configuration.
        """
        self.tracker_id = tracker_id
        self.source = source
        self.source_type = source_type
        self.queries = queries
        self.interval = interval
        self.storage = storage

        self.values = []
        self.last_modified = 0
        interval = 0


    def get_id(self):
        """Return a string with unique tracker ID.
        """
        return self.tracker_id

    def _grab_data(self):
        """Grab data from datasource.
        """
        ds = get_data_source(self.source)
        self._raw_data = ds.grab_data()

    def _parse_data(self):
        """Parse raw data with appropriate parser and save gathered values in
        `values` attribute.
        """
        self._parser = get_parser(self.source_type)
        self._parser.initialize()
        self._parser.parse(self._raw_data)
        self._clean_data = [self._parser.xpath(query)
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

    def _process_datasource_exception(self, e):
        # TODO: process exception here
        print 'DATASOURCE EXCEPTION', type(e)


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
        except BaseGrabError, e:
            self._process_datasource_exception(e)

        # TODO: wee need to handle all errors which can occure.

        finally:
            self.last_modified = time.time()

