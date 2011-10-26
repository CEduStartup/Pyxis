from shared.trackers.datasources.constants import HTTP_DATASOURCE
from shared.trackers.data_types import XML_DATA
import json


SAMPLE_URI = 'http://service.com/resource'

SETTINGS = {'access_method': HTTP_DATASOURCE,
            'query': json.dumps({'URI': SAMPLE_URI})}

XML_SETTINGS = {'access_method': HTTP_DATASOURCE,
                'query': json.dumps({'URI': SAMPLE_URI}),
                'datatype': XML_DATA}

RESULT_DATA = 'RAW_DATA_ENCODED'

class DummyEventSender:
    events = []

    def fire(self, event_name, **params): 
        DummyEventSender.events.append((event_name, params))

class DummyURLLib2:
    HTTPError, URLError = 1, 2
    
    class Reader:
        code = 200
        
        def read(*args):
            return RESULT_DATA
    
    @classmethod
    def Request(*args, **kwargs):
        pass
        
    @classmethod
    def urlopen(*args, **kwargs):
        return DummyURLLib2.Reader()