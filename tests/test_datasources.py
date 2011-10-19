from shared.trackers.datasources.constants import HTTP_DATASOURCE

import unittest
import json

SAMPLE_URI = 'http://service.com/resource'

SETTINGS = {'access_method': HTTP_DATASOURCE,
            'query': json.dumps({'URI': SAMPLE_URI})}

RESULT_DATA = 'RAW_DATA_ENCODED'

class DummyEventSender:
    def fire(self, *args, **kwargs): pass

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

class DatasourcesTest(unittest.TestCase):
    Orig_Event_Sender, Orig_urllib2 = None, None
    get_datasource = None
    
    def setUp(self):
        from shared.events import EventManager
        self.Orig_EventSender = EventManager.EventSender
        EventManager.EventSender = DummyEventSender
        
        from shared.trackers.datasources.factory import get_datasource
        self.get_datasource = get_datasource
        
        from shared.trackers.datasources import HTTP
        self.Orig_urllib2 = HTTP.urllib2
        HTTP.urllib2 = DummyURLLib2
        
    def test_datasource_init(self):
        datasource = self.get_datasource(SETTINGS)
        self.assertEqual(datasource.__class__.__name__, 'DatasourceHTTP')
        self.assertEqual(datasource._target, SAMPLE_URI)
    
    def test_grab_data(self):
        datasource = self.get_datasource(SETTINGS)
        raw_data = datasource.grab_data()
        self.assertEqual(raw_data, RESULT_DATA)
        self.assertEqual(datasource.response_code, 200)
    
    def tearDown(self):
        from shared.events import EventManager
        EventManager.EventSender = self.Orig_EventSender
        from shared.trackers.datasources import HTTP
        HTTP.urllib2 = self.Orig_urllib2

datasources_tests = unittest.TestSuite()
loader = unittest.TestLoader()
datasources_tests.addTests(loader.loadTestsFromTestCase(DatasourcesTest))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(datasources_tests)