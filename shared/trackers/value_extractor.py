# coding=utf-8

"""This module contains functionality for extracting values from data received
from parsers.
"""

import re

from shared.trackers import INT_VALUE_TYPE, FLOAT_VALUE_TYPE


class ValueExtractionError(Exception):
    pass


class ValueExtractor:
    """This class mission is to extract numeric value from data received from
    parser. For example, parser returned XML node value: 8,01UAH. This cannot
    be used as a number, so we need to extract number from given value.

    That's what this class is intended for.
    """

    def extract_value(self, text, value_type):
        """Extract number from parser results.

        :Parameters:
            - `value`: raw value
            - `value_type`: type of value (int, float, etc.)
        """
        try:
            value = self._find_numeric_value(text)
            if value_type == INT_VALUE_TYPE:
                value = self._remove_delimiters(value)
                clean_value = int(value)
            elif value_type == FLOAT_VALUE_TYPE:
                value = value.replace(',', '.')
                clean_value = float(value)
            else:
                raise ValueExtractionError('Unknown value type %s' %
                                           (value_type,))
        except (ValueError, UnicodeEncodeError):
            raise ValueExtractionError('Cannot extract number from: %s' %
                                       (text,))

        return clean_value

    def _find_numeric_value(self, text):
        regex = re.compile(r'-?(?:\d[,.]?)*\d')
        found = regex.findall(text)
        if found:
            # TODO: probably in some cases we need to return all numbers which
            # we found and let the user to decide which is desirable.
            return found[-1]
        return ''

    def _remove_delimiters(self, value):
        return value.replace(',', '').replace('.', '')


if __name__ == '__main__':
    ve = ValueExtractor()
    print ve.extract_value('8,01', 'float')
    print ve.extract_value('24 338 специалистов', 'int')
