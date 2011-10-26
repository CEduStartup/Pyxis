import unittest
from dummy_test_classes.datasources import SAMPLE_URI, XML_SETTINGS, RESULT_DATA, \
                                           DummyEventSender, DummyURLLib2

class TrackerTest(unittest.TestCase):
    Orig_Event_Sender, Orig_urllib2 = None, None
    get_datasource = None
    
    def setUp(self):
        from shared.events import EventManager
        self.Orig_EventSender = EventManager.EventSender
        EventManager.EventSender = DummyEventSender

        global Tracker
        from shared.trackers.Tracker import Tracker
        
        from shared.trackers.datasources import HTTP
        self.Orig_urllib2 = HTTP.urllib2
        HTTP.urllib2 = DummyURLLib2

    def test_repr(self):
        tracker = Tracker('tracker_id_1', 15, [], tracker_name='dummy')
        self.assertEquals(repr(tracker), '<Tracker tracker_id_1: `dummy` []>')
        
    def test_wrong_configuration(self):
        tracker = Tracker('tracker_id_1', 15, [], tracker_name='dummy')
        tracker.process()
        try:
            event = DummyEventSender.events.pop()
            self.assertEquals(event[0], 'LOGGER.CRITICAL')
        except IndexError:
            self.fail('No event was sent')
    
    def test_process(self):
        tracker = Tracker('tracker_id_1', 15, XML_SETTINGS, tracker_name='dummy')
        tracker.process()     
        print DummyEventSender.events   

    def tearDown(self):
        from shared.events import EventManager
        EventManager.EventSender = self.Orig_EventSender


tracker_tests = unittest.TestSuite()
loader = unittest.TestLoader()
tracker_tests.addTests(loader.loadTestsFromTestCase(TrackerTest))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(tracker_tests)