from shared.trackers.datasources.constants import HTTP_DATASOURCE
from shared.trackers.data_types import XML_DATA
import json


SAMPLE_URI = 'http://service.com/resource'

SETTINGS = {'access_method': HTTP_DATASOURCE,
            'query': json.dumps({'URI': SAMPLE_URI})}

XPATH1 = '//XPATH1'
XPATH2 = '//XPATH2'

XPATH_VALUES = {
    XPATH1: 111,
    XPATH2: 222
}

XML_SETTINGS = {'access_method': HTTP_DATASOURCE,
                'query': json.dumps({'URI': SAMPLE_URI}),
                'datatype': XML_DATA,
                'values': [{
                    'value_id': 1,
                    'type': 'int',
                    'extraction_rule': XPATH1
                }]}
                
XML_SETTINGS_TWO_VALUES = {
                'access_method': HTTP_DATASOURCE,
                'query': json.dumps({'URI': SAMPLE_URI}),
                'datatype': XML_DATA,
                'values': [
                    {'value_id': 1, 'type': 'int', 'extraction_rule': XPATH1}, 
                    {'value_id': 2, 'type': 'int', 'extraction_rule': XPATH2}, 
                ]}

RESULT_DATA = 'RAW_DATA_ENCODED'

def dummy_get_parser(data_type):
    if data_type == XML_DATA:
        return DummyXMLParser()
    else:
        raise Exception('Wrong data type')

class DummyXMLParser:
    def initialize(self):
        pass
    
    def parse(self, xml):
        if not xml == RESULT_DATA:
            raise Exception('Wrong format')
        
    def xpath(self, xpath):
        return XPATH_VALUES[xpath]

class DummyEventSender:
    events = []

    def fire(self, event_name, **params): 
        DummyEventSender.events.append((event_name, params))
        
class DummyStorage:
    tracker = None
    data = {}

    def put(self, tracker, data):
        self.tracker = tracker
        self.data = data

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