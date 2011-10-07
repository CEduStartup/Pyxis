"""This module contains a base class for all datasources which use HTTP
protocol to grab data.
"""

from datasources import DatasourceCommon


class DatasourceHTTP(DatasourceCommon):

    def initialize(self):
        pass

    def grab_data(self):
        pass

