# coding=utf-8
import re

## Pyxis project, value extractor module.
##
##

class ValueExtractionError(Exception):
    pass


class ValueExtractor:
    """This class mission is to extract numeric value from data received from
    parser. For example, parser returned XML node value: 8,01UAH. This cannot
    be used as a number, so we need to extract number from given value.

    That's what this class is intended for.
    """

    def extract_number(self, text, value_type):
        """Extract number from parser results.

        :Parameters:
            - `value`: raw value
            - `value_type`: type of value (int, float, etc.)
        """
        try:
            value = self._find_numeric_value(text)
            if value_type == 'int':
                value = self._remove_delimiters(value)
                clean_value = int(value)
            elif value_type == 'float':
                value = value.replace(',', '.')
                clean_value = float(value)
        except (ValueError, UnicodeEncodeError):
            raise ValueError('Cannot extract number')

        return clean_value

    def _find_numeric_value(self, text):
        regex = re.compile('-?(?:\d[,.]?)*\d')
        found = regex.findall(r'%s' %text)
        if found:
            return found[-1]
        return ''

    def _remove_delimiters(self, value):
        return value.replace(',', '').replace('.', '')


if __name__ == '__main__':
    ve = ValueExtractor()
    print ve.extract_number('8,01', 'float')
    print ve.extract_number('24 338 специалистов', 'int')
