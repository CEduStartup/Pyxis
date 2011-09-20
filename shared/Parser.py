"""This module contains different data parsers compatible with `gevent`.

Don't create parser instance manually, rather use `get_parser()` factory
method.
"""

import abc
import BeautifulSoup
import gevent
import StringIO

import target

from lxml import etree, html
from lxml.html import soupparser


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

class GBeautifulSoupParser(BeautifulSoup.BeautifulSoup):

    """This is a modification of `BeautifulSoup` parser which is compatible
    with gevent.

    This class has `parse_starttag()` method rewritten so it returns control to
    gevent (by calling `gevent.sleep(0)`) when `TAGS_IN_ROUND` tags are parsed.
    """

    def __init__(self, *args, **kwargs):
        self._tags_parsed = 0
        BeautifulSoup.BeautifulSoup.__init__(self, *args, **kwargs)

    # How many tags will be parsed before switching control to gevent.
    TAGS_IN_ROUND = 50

    def parse_starttag(self, start_pos):
        """Handle `starttag` event.
        """
        # Check if we need to return control to gevent.
        if self._tags_parsed == self.TAGS_IN_ROUND:
            self._tags_parsed = 0
            gevent.sleep(0)

        self._tags_parsed += 1

        return BeautifulSoup.BeautifulSoup.parse_starttag(self, start_pos)


class XMLParser(BaseParser):

    """XML parser compatible with `gevent`.
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
        self._parser = GBeautifulSoupParser

    def _parse(self, data):
        """Please see description of the method in parent class: `XMLParser`.
        """
        return html.soupparser.parse(data, beautifulsoup=self._parser)


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
    p = get_parser('html')
    p.initialize()
    data = ' '.join(open('index.html').readlines())
    p.parse(data)
    print p._etree_dom
