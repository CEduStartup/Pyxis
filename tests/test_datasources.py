import unittest
from dummy_test_classes.datasources import SAMPLE_URI, SETTINGS, RESULT_DATA, \
                                           DummyEventSender, DummyURLLib2


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
        datasource.grab_data()
        raw_data = datasource.get_raw_data()
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