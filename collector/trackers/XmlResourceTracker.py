from . import HttpResourceTracker
from config import logger

from shared.Parser import get_parser

class XmlResourceTracker(HttpResourceTracker):
    """
    This class implements xml resource tracking in parse_data method.
    html contains string representation of xml document, result
    is stored to data['value'].
    """

    def parse_data(self, data, html):
        def cast(l):
            return dict((k, v) for k,v in enumerate(l))

        xml_parser = get_parser('xml')
        xml_parser.initialize()
        xml_parser.parse(html)
        what = '//TEMPERATURE/@max'
        found = xml_parser.xpath(what, cast=cast)

        data.update(found)
        logger.info('parse - tracker: %s (%s), data: %s, xpath: %s, found: %s'
                    % (self.get_id(), self.get_source(), data, what, found))

