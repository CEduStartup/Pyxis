from . import HttpResourceTracker

class XmlResourceTracker(HttpResourceTracker):
    """
    This class implements xml resource tracking in parse_data method.
    html contains string representation of xml document, result
    is stored to data['value'].
    """

    def parse_data(self, data, html):
        pass