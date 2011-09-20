"""This module contains different `gevent` compatible parsers for `lxml` lib
"""

import abc
import StringIO

import target

from lxml import etree, html


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

    def _parse(self, data):
        """Low-level parse method. Do all work.

        :Parameters:
            - `data`: raw data with interface compatible to `StringIO.StringIO`

        :Return:
            - `etree.Element` object with parsed data.

        :Exception:
            - Various `lxml` parser-related exceptions. Please see lxml
              documentation from more details.
        """
        return etree.parse(data, self._parser)


    def parse(self, raw_data):
        """Parse `raw_data` and return XML DOM compatible with `lxml.etree`.
        """
        try:
            self._etree_dom = self._parse(StringIO.StringIO(raw_data))
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


class HTMLParser(XMLParser):

    """HTML parser.

    Don't create it directly use `get_parser()` factory method.
    """

    def initialize(self):
        html_target = target.geventTreeBuilder()
        self._parser = etree.HTMLParser(target=html_target)

    def _parse(self, data):
        """Please see description of the method in parent class: `XMLParser`.
        """
        return html.parse(data, self._parser)


# Maps datatype to parser class which can handle it.
_PARSER_TYPES_MAPPING = {
    'xml': XMLParser,
    'html': HTMLParser,
}

def get_parser(datatype='xml'):
    """Return `lxml` compatible parsers.

    :Parameters:
        - `datatype`: string which contains datatype. Currently it's one of the
          following: 'xml', 'html', 'json'.
    """
    return _PARSER_TYPES_MAPPING[datatype]()

if __name__ == '__main__':

    def cast_join(l):
        return '\n'.join(l)

    raw_data = '\n'.join(open('xml.xml').readlines())
    raw_data2 = '\n'.join(open('index.html').readlines())
    p = get_parser(datatype='xml')
    p2 = get_parser(datatype='html')
    p.initialize()
    p2.initialize()
    try:
        p.parse(raw_data)
        p2.parse(raw_data2)
    except ParserError, e:
        print 'Error Details:', getattr(e, 'description', 'No details.')
        import sys; sys.exit(1)
    print p.xpath('/root/a/@name', cast=cast_join)
    print p2.xpath(
       '/html/body/div[2]/div[2]/div[3]/text()')[0]
