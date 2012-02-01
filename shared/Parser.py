"""This module contains different data parsers.

Don't create parser instance manually, rather use `get_parser()` factory
method.
"""

import abc
import BeautifulSoup
import csv
import gevent
import StringIO

from lxml import etree
from lxml.html import soupparser

from shared.trackers.value_extractor import (ValueExtractor,
                                             ValueExtractionError)
from shared.trackers import (XML_DATA_TYPE, HTML_DATA_TYPE, JSON_DATA_TYPE,
                             CSV_DATA_TYPE)

# Determine how many tags will be parser before return control to gevent()
ELEMENTS_IN_ROUND = 50


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

class ParserCastError(ParserError):

    """Indicates that gathered value cannot be casted to desirable type.
    """


class GTreeBuilder(etree.TreeBuilder):

    """This class do the same work as `etree.TreeBuilder` but it's compatible
    with gevent.
    """

    def __init__(self, max_elements=ELEMENTS_IN_ROUND):
        etree.TreeBuilder.__init__(self)
        self._elements_in_round = max_elements
        self._elements_parsed = 0

    def start(self, tag, attrs):
        if self._elements_parsed == self._elements_in_round:
            self._elements_parsed = 0
            gevent.sleep(0)

        self._elements_parsed += 1
        return etree.TreeBuilder.start(self, tag, attrs)


def _check_initialization(method):
    """Check if the parser is initialized.

    :Return:
        - `None`

    :Exception:
        - `ParserNotInitializedError`: in case when `._parser` attribute is
          `None`.
    """
    def check(self, *args, **kwargs):
        """Inner check method. Check if the parser is initialize and if not
        then raise execption.
        """
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

    @abc.abstractmethod
    def get_parsed(self):
        """Getter for parsed data.
        """

    def _cast_value(self, raw_value, value_type=None, cast=None, **kwargs):
        """Cast the value using predefined datatypes and/or custom `cast`
        method callable object.

        :Parameters:
            - `raw_value`: raw value returned by parser.
            - `value_type`: predefined value type defined in `shared.trackers`
              module e.g.: INT_VALUE_TYPE, FLOAT_VALUE_TYPE, or `None` to skip
              casting to predefined type or you need custom casting.
            - `cast`: callable object which will be used for casting. Must
              accept at least 1 non-keyword argument: raw value, and returns
              cleaned data. Also it can accept keyword arguments which needs to
              be passed as `kwargs`. In case when it's impossible to cast that
              value `cast` method must raise
              `shared.trackers.value_extractor.ValueExtractionError` exception.
            - `**kwargs`: keyword arguments which will be passed to `cast` object.
        """
        extractor = ValueExtractor()

        def _process_value(val):
            clean_value = val
            if value_type is not None:
                clean_value = extractor.extract_value(val, value_type)

            if cast is not None:
                clean_value = cast(clean_value, **kwargs)

            return clean_value

        try:
            if isinstance(raw_value, (list, tuple)):
                return [_process_value(v) for v in raw_value]

            return _process_value(raw_value)
        except ValueExtractionError, err:
            raise ParserCastError(err)

    @abc.abstractmethod
    def get_value(self, query, value_type=None, cast=None, **kwargs):
        """Return single value from parsed data, using some query to find it.

        :Parameters:
            - `query`: a query which will be used to find some value e.g. xpath
              for XML and HTML, or column and row numbers for CSV.
            - `datatype`: one of datatypes defined in `shared.trackers` e.g.
              INT_VALUE_TYPE, FLOAT_VALUE_TYPE, or `None`.
            - `cast`: a callable objects which will be used to cast the value
              (or None to skip casting).
            - `kwargs`: arguments required by `cast` function.
        """
##        raw_value = self.get_parsed()
##        return self._cast_value(raw_value, value_type=value_type,
##                                cast=cast, **kwargs)

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
    TAGS_IN_ROUND = ELEMENTS_IN_ROUND

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

    def get_parsed(self):
        """Getter for DOM tree of XML.
        """
        return self._etree_dom

    def xpath(self, xpath_str):
        """Return information from XML using XPath.

        :Parameters:
            - `xpath_str`: string which contains xpath path to the data.

        :Return:
            - Return a list of strings. Each string represent 1 element from
              XML document.
        """
        return self._etree_dom.xpath(xpath_str)

    def get_value(self, xpath_str, value_type=None, cast=None, **kwargs):
        """Return the value of element defined by xpath.

        :Parameters:
            - `xpath_str`: string which contains xpath.
        """
        data = self.xpath(xpath_str)
        return self._cast_value(data, value_type=value_type,
                                cast=cast, **kwargs)

class GXMLParser(XMLParser):

    """XML parser compatible with `gevent`.
    """

    def _create_parser(self):
        """Prepare parser to work.
        """
        xml_target = GTreeBuilder()
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

    def _cast_value(self, raw_value, value_type=None, cast=None, **kwargs):
        """Cast BeautifulSoup elements to text.
        """
        if isinstance(raw_value, (tuple, list)):
            dir(raw_value[0])
            raw_value = [x.text for x in raw_value]
        else:
            dir(raw_value)
            raw_value = raw_value.text

        return XMLParser._cast_value(self, raw_value, value_type=value_type,
                                     cast=cast, **kwargs)


class GHTMLParser(HTMLParser):

    """HTML parser.
    """

    def _create_parser(self):
        self._parser = GBeautifulSoupParser


class CSVParser(BaseParser):

    """This class is capable to parse CSV files.

    NOTE:
    http://chartapi.finance.yahoo.com/instrument/1.0/ACC.NS/chartdata;type=quote;range=1d/csv/
    """

    def __init__(self):
        """CSVParser constructor.
        """
        BaseParser.__init__(self)
        self._parser = None
        self._dialect = None
        self._parsed_data = None
        self._has_header = None

    def _initialize(self, raw_data):
        """Detect CSV dialect and prepare data to parsing.
        """
        self._detect_dialect(raw_data.read(1024))
        raw_data.seek(0)

    def _create_parser(self):
        """This is a fake method. We need it only to be able to instantiate an
        instance of this class, because in parent class this method marked as
        abstract.
        """

    def _detect_dialect(self, raw_data_sample):
        """Try to automatically detect the dialect of CSV data.

        :Parameters:
            - `raw_data_sample` a string which contains very first.

        """
        sniffer = csv.Sniffer()
        self._dialect = sniffer.sniff(raw_data_sample)
        self._has_header = sniffer.has_header

    def initialize(self, raw_data):
        """Initialize CSV parser.

        :Parameters:
            - `raw_data`: a file-like object (probably StringIO) which provides
              `read()` and `seek()` methods and contains raw CSV data.
        """
        self._initialize(raw_data)

    def parse(self, raw_data):
        """Main method for parsing.
        """
        self._parsed_data = self._parse(raw_data)

    def _parse(self, raw_data):
        """Inner parser implementation.
        """
        self._parser = csv.reader(raw_data, self._dialect)
        return [row for row in self._parser]

    def get_value(self, position, cast=None):
        """Return a data from cell.

        :Parameters:
            - `position`: tuple of the following structure: ::

                (
                  row_number: row number starting from 0,
                  col_number: column number starting from 0
                )
        """
        row_no, col_no = position
        data = self._parsed_data[row_no][col_no]
        return self._cast_value(data, cast=cast)

    def get_parsed(self):
        """Return parsed data.
        """
        return self._parsed_data


# Maps datatype to parser class which can handle it.
_PARSER_TYPES_MAPPING = {
    'plain': {
        XML_DATA_TYPE: XMLParser,
        HTML_DATA_TYPE: HTMLParser,
        CSV_DATA_TYPE: CSVParser,
    },

    'gevent_safe': {
        XML_DATA_TYPE: GXMLParser,
        HTML_DATA_TYPE: GHTMLParser,
        CSV_DATA_TYPE: CSVParser,
    }
}

def get_parser(datatype, gevent_safe=True):
    """Return `lxml` compatible parsers.

    :Parameters:
        - `datatype`: string which contains datatype. Currently it's one of the
          following: XML_DATA, JSON_DATA, HTML_DATA.
        - `gevent_safe`: boolean. If `True` then this method will *always*
          return parser instance which is compatible with gevent.

    :Return:
        - An instance of a parser compatible with the given `datatype`.
    """
    threads_type = 'gevent_safe'
    if not gevent_safe:
        threads_type = 'plain'

    return _PARSER_TYPES_MAPPING[threads_type][datatype]()

if __name__ == '__main__':
    d = open('t/xml.xml')
    p = get_parser('xml', gevent_safe=False)
    p.initialize()
    p.parse(' '.join(d.readlines()))
    d.close()
    print p.xpath('//TEMPERATURE/@max')
