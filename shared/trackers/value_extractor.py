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

    def extract_number(self, value, value_type):
        """Extract number from parser results.

        :Parameters:
            - `value`: raw value
            - `value_type`: type of value (int, float, etc.)
        """
        clean_value = None
        print '00000000000000000000000000000', value, value_type
        if value_type == 'int':
            value = self._remove_delimiters(value)
            clean_value = int(value)
            print '111111111111111111111111', clean_value
        elif value_type == 'float':
            value = value.replace(',', '.')
            clean_value = float(value)
            print '222222222222222222222222', clean_value
        return clean_value

    def _remove_delimiters(self, value):
        return value.replace(',', '').replace('.', '')

    def _cast_float(value):
        return int(float(value.replace(',', '.')))


if __name__ == '__main__':
    ve = ValueExtractor()
    print ve.extract_number('8,01', 'float')
    print ve.extract_number('1,000,000,000', 'int')
