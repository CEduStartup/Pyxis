import multiprocessing as mp
import pickle
import unittest
from shared.events import Event
from unittest_utils import dict_equals

class EventsTest(unittest.TestCase):
    def setUp(self):
        print

    def test_serialization(self):
        event = Event.LoggerInfoEvent(message='Test Message')
        try:
            unserialized_event = pickle.loads(pickle.dumps(event))
        except Exception:
            self.fail('No exception expected')
        self.assertTrue(dict_equals(event.__dict__ ,unserialized_event.__dict__))
        
    def test_multi_serialization(self):
        event = Event.LoggerInfoEvent(message='Test Message')
        try:
            pickled = pickle.dumps(event)
            unserialized_event = pickle.loads(pickle.dumps(pickle.loads(pickled)))
        except Exception, e:
            print e
            self.fail('No exception expected')
        self.assertTrue(dict_equals(event.__dict__ ,unserialized_event.__dict__))            
    
    def test_logger_info_event(self):
        msg = 'Test Message'
        event = Event.LoggerInfoEvent(message=msg)
        self.assertTrue(event.format_message() == msg)
        unserialized_event = pickle.loads(pickle.dumps(event))
        self.assertTrue(unserialized_event.format_message() == msg)
            
            
events_tests = unittest.TestSuite()
loader = unittest.TestLoader()
events_tests.addTests(loader.loadTestsFromTestCase(EventsTest))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(events_tests)