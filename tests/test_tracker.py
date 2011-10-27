import unittest
from dummy_test_classes.datasources import SAMPLE_URI, XML_SETTINGS, XML_SETTINGS_TWO_VALUES, RESULT_DATA, \
                                           DummyEventSender, DummyURLLib2, \
                                           dummy_get_parser, DummyStorage, \
                                           XPATH1, XPATH2, XPATH_VALUES

class TrackerTest(unittest.TestCase):
    Orig_Event_Sender, Orig_urllib2, Orig_get_parser = None, None, None
    
    def setUp(self):
        from shared.events import EventManager
        self.Orig_EventSender = EventManager.EventSender
        EventManager.EventSender = DummyEventSender
        DummyEventSender.events = []
        
        from shared import Parser
        Orig_get_parser = Parser.get_parser
        Parser.get_parser = dummy_get_parser
        
        global Tracker
        from shared.trackers.Tracker import Tracker
        
        from shared.trackers.datasources import HTTP
        self.Orig_urllib2 = HTTP.urllib2
        HTTP.urllib2 = DummyURLLib2

    def test_repr(self):
        tracker = Tracker('tracker_id_1', 15, [], tracker_name='dummy')
        self.assertEquals(repr(tracker), '<Tracker tracker_id_1: `dummy` []>')
        
    def test_wrong_configuration(self):
        tracker = Tracker('tracker_id_1', 15, {'some wrong config': '11'}, tracker_name='dummy')
        tracker.set_storage(DummyStorage())
        tracker.process()
        try:
            error = DummyEventSender.events.pop()
            self.assertEquals(error[0], 'LOGGER.CRITICAL')
        except IndexError:
            self.fail('Waiting for event')
    
    def test_process(self):
        storage = DummyStorage()
        tracker = Tracker('tracker_id_1', 15, XML_SETTINGS, tracker_name='dummy')
        tracker.set_storage(storage)
        tracker.process() 
        self.assertTrue('timestamp' in storage.data and storage.data['timestamp'] > 0)
        self.assertEquals(storage.data['data'], {1: XPATH_VALUES[XPATH1]})
    
    def test_process_two_values(self):
        storage = DummyStorage()
        tracker = Tracker('tracker_id_1', 15, XML_SETTINGS_TWO_VALUES, tracker_name='dummy')
        tracker.set_storage(storage)
        tracker.process()
        self.assertTrue('timestamp' in storage.data and storage.data['timestamp'] > 0)
        self.assertEquals(storage.data['data'], {1: XPATH_VALUES[XPATH1], 
                                                 2: XPATH_VALUES[XPATH2]})
                                                
    def tearDown(self):
        from shared.events import EventManager
        EventManager.EventSender = self.Orig_EventSender

        from shared import Parser
        Parser.get_parser = self.Orig_get_parser
        
        if [event[0] for event in DummyEventSender.events if event[0] == 'LOGGER.CRITICAL']:
            #print event
            self.fail('LOGGER.CRITICAL event was sent')


tracker_tests = unittest.TestSuite()
loader = unittest.TestLoader()
tracker_tests.addTests(loader.loadTestsFromTestCase(TrackerTest))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(tracker_tests)