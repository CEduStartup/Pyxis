import unittest
import sys
from Queue import Queue

class TestBeanstalkc:
    UnexpectedResponse, CommandFailed = None, None
    class Connection:
        queue = None
        def __init__(self, *args, **kwargs):
            if not self.__class__.queue:
                self.__class__.queue = Queue()
            
        def connect(self, *args, **kwargs): pass
            
        def close(self, *args, **kwargs): pass
            
        def use(self, *args, **kwargs): pass
        
        def put(self, object):
            self.queue.put(object)
        
        def reserve(self):
            return self.queue.get_nowait()




from logger.manager import LogManager
from shared.events.EventManager import EventSender, EventReceiver
import shared.events.EventManager as EventManager

class LogManagerTest(unittest.TestCase):
    def setUp(self):
        self.original_beanstalkc = EventManager.beanstalkc
        EventManager.beanstalkc = self.beanstalkc = TestBeanstalkc()
    
    def test_log_manager(self):
        log_mgr = LogManager('localhost', 9999)
        self.sender = EventSender()
        self.sender.fire('LOGGER.INFO', message='Message1')
        log_mgr.receiver._client.reserve()

    def tearDown(self):
        EventManager.beanstalkc = self.original_beanstalkc

logmanager_tests = unittest.TestSuite()
loader = unittest.TestLoader()
logmanager_tests.addTests(loader.loadTestsFromTestCase(LogManagerTest))

if __name__ == '__main__':
    # Run
    unittest.TextTestRunner(verbosity=2).run(logmanager_tests)
