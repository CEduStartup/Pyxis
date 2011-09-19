"""This module contains different `gevent` compatible parsers for `lxml` lib
"""

import abc
import StringIO

import target

from lxml import etree


class ParserError(Exception):

    """Base class for all parser errors.
    """

class ParserSyntaxError(ParserError):

    """This class describes all syntax errors which can occur during data
    parsing.

    Please use `description` attribute to get error details.
    """

    def __init__(self, details=''):
        ParserError.__init__(self),
        self.description = details


class BaseParser(object):

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

        :Return:
            - `None`

        :Exceptions:
            - `ParserSyntaxError`: in case when `raw_data` cannot be parsed
              because of critical syntax error.
        """

class XMLParser(BaseParser):

    """XML parser.
    Don't create it directly. Use `get_parser()` factory method.
    """

    def __init__(self):
        BaseParser.__init__(self)
        self._etree_dom = None

    def initialize(self):
        """Prepare parser to work.
        """
        xml_target = target.geventTreeBuilder()
        self._parser = etree.XMLParser(target=xml_target)

    def parse(self, raw_data):
        """Parse `raw_data` and return XML DOM compatible with `lxml.etree`.
        """
        try:
            self._etree_dom = etree.parse(StringIO.StringIO(raw_data),
                                          self._parser)
        except etree.XMLSyntaxError, e:
            # Currently it's enought to return information only about fatal
            # errors.
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            raise ParserSyntaxError(details=str(log))

    def xpath(self, xpath_str, cast=None):
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
    try:
        p.parse(raw_data)
    except ParserError, e:
        print 'Error Details:', getattr(e, 'description', 'No details.')
        import sys; sys.exit(1)
    print p.get_xpath_node('/root/a/@name', cast=str)
