"""This module contains different data parsers.

Don't create parser instance manually, rather use `get_parser()` factory
method. It will decide whether you need gevent compatible parser or not base on
your global namespace. If `gevent` is imported in it, `get_parser()` would
return an gevent compatible instance of a parser.
"""

import abc
import BeautifulSoup
import gevent
import StringIO

from lxml import etree, html
from lxml.html import soupparser

from shared import target

class ParserError(Exception):

    """Base class for all parser errors.
    """

class ParserNotInitializedError(ParserError):

    """Operation with not initialized parser.
    """

class ParserSyntaxError(ParserError):

    """This class describes all syntax errors which can occur during data
    parsing.

    print p1.xpath('//TEMPERATURE/@max')
    Please use `description` attribute to get error details.
    """

    def __init__(self, details=''):
        ParserError.__init__(self),
        self.description = details


def _check_initialization(method):
    """Check if the parser is initialized.

    :Return:
        - `None`

    :Exception:
        - `ParserNotInitializedError`: in case when `._parser` attribute is
          `None`.
    """
    def check(self, *args, **kwargs):
        if self._parser is None:
            raise ParserNotInitializedError()
        return method(self, *args, **kwargs)

    return check


class BaseParser(object):

    """Base class for all parsers.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._parser = None

    def initialize(self):
        """Create and initialize parser.
        """
        self._create_parser()
        self._initialize()

    def _initialize(self):
        """Responsible for custom parser initialization. You can overwrite
        this method in child class.
        """
        pass

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

    @abc.abstractmethod
    def _create_parser(self):
        """This method responsible for parser creation. You need to overwrite
        this method in your class.
        """
        self._parser = None

    @abc.abstractmethod
    def _parse(self, raw_data):
        """Inner implementation of the parser.
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

    """XML parser which is not compatible with gevent.
    """

    def __init__(self):
        BaseParser.__init__(self)
        self._etree_dom = None

    def _create_parser(self):
        """Create XML parser.
        """
        xml_target = etree.TreeBuilder()
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

    @_check_initialization
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


class GXMLParser(XMLParser):

    """XML parser compatible with `gevent`.
    """

    def _create_parser(self):
        """Prepare parser to work.
        """
        xml_target = target.geventTreeBuilder()
        self._parser = etree.XMLParser(target=xml_target)


class HTMLParser(XMLParser):

    """HTML parser.
    """

    def _create_parser(self):
        self._parser = BeautifulSoup.BeautifulSoup

    def _parse(self, data):
        """Parse the document `data` and return result (`ElementTree` object).
        """
        return soupparser.parse(data, beautifulsoup=self._parser)

    def parse(self, data):
        """High level parse method. Parse document, handle errors. Assign
        parsing result (`lxml.etree.ElementTree` object) to `_etree_dom`
        attribute.
        """
        # TODO: Add errors handling.
        self._etree_dom = self._parse(StringIO.StringIO(data))


class GHTMLParser(HTMLParser):

    """HTML parser.
    """

    def _create_parser(self):
        self._parser = GBeautifulSoupParser


# Maps datatype to parser class which can handle it.
_PARSER_TYPES_MAPPING = {
    'plain': {
        'xml': XMLParser,
        'html': HTMLParser,
    },

    'gevent_safe': {
        'xml': GXMLParser,
        'html': GHTMLParser,
    }
}

def get_parser(datatype='xml', gevent_safe=True):
    """Return `lxml` compatible parsers.

    :Parameters:
        - `datatype`: string which contains datatype. Currently it's one of the
          following: 'xml', 'html', 'json'.
        - `gevent_safe`: boolean. If `True` then this method will *always*
          return parser instance which is compatible with gevent.

    :Return:
        - An instance of a parser compatible with the given `datatype`.
    """
    threads_type = 'gevent_safe'
    if not gevent_safe:
        threads_type = 'plain'

    return _PARSER_TYPES_MAPPING[threads_type][datatype]()

