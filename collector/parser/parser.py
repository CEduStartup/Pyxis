"""This module contains different `gevent` compatible parsers for `lxml` lib
"""

import abc
import StringIO

import target

from lxml import etree


class baseParser(object):

    """Base class for all parsers.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
       self._parser = None

    @abc.abstractmethod
    def initialize(self):
        """Create and initialize parser.
        """

    @abc.abstractmethod
    def parse(self, raw_data):
        """Return parsing results.
        Use this method to parse `raw_data`.
        """

class XMLParser(baseParser):

    """XML parser.
    Don't create it directly. Use `get_parser()` factory method.
    """

    def __init__(self):
        baseParser.__init__(self)
        self._etree_dom = None

    def initialize(self):
        """Prepare parser to work.
        """
        xml_target = target.geventTreeBuilder()
        self._parser = etree.XMLParser(target=xml_target)

    def parse(self, raw_data):
        """Parse `raw_data` and return XML DOM compatible with `lxml.etree`.
        """
        self._etree_dom = etree.parse(StringIO.StringIO(raw_data), self._parser)
        return self._etree_dom

    def get_xpath_node(self, xpath_str, cast=None):
        """Return information from XML using XPath.

        :Parameters:
            - `xpath_str`: string which contains xpath path to the data.
            - `cast`: callable object which will be used to convert information
              to the required type.

        :Return:
            - Return a list of strings. Each string represent 1 element from
              XML document.
        """
        data = self._etree_dom.xpath(xpath_str)

        if cast is not None:
            return cast(data)

        return data


# Maps datatype to parser class which can handle it.
_PARSER_TYPES_MAPPING = {
    'xml': XMLParser,
}

def get_parser(datatype='xml'):
    """Return `lxml` compatible parsers.

    :Parameters:
        - `datatype`: string which contains datatype. Currently it's one of the
          following: 'xml', 'html', 'json'.
    """
    return _PARSER_TYPES_MAPPING[datatype]()

if __name__ == '__main__':
    raw_data = '\n'.join(open('xml.xml').readlines())
    p = get_parser(datatype='xml')
    p.initialize()
    p.parse(raw_data)
    print p.get_xpath_node('/root/a/@name', cast=str)
