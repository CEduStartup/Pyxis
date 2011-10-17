"""This module contains base class for all datasources.
If you want to create your own datasource, please subclass `DatasourceCommon`
or one of the above classes.
"""

from abc import ABCMeta, abstractmethod


class DatasourceCommon(object):

    """This is the base class for all datasources.
    Its main method is `grab_data()` grabs raw data from the source.

    :Instance variables:

        - `grab_spent_time`: `float`. How many time was spent while grabbing
          data.
        - `raw_data_size`: `int`. Size of `raw_data` in bytes.
        - `raw_data`: `str`: Contains raw data grabbed from the source.

    """

    __metaclass__ = ABCMeta

    grab_spent_time = None
    raw_data_size = None
    raw_data = None

    def __init__(self, target):
        """Initialize class instance with valid configuration.
        """
        self._target = target

    @abstractmethod
    def initialize(self):
        """This method is responsible for datasource initialization and must be
        rewritten in child classes.
        """
        pass

    @abstractmethod
    def grab_data(self):
        """This method return raw data grabbed from the `self._target`.
        """
        pass

