import unittest

from shared.events.Event import EventMeta


class EventMetaTestCase(unittest.TestCase):
    def test_empty_eid(self):
        class TestEvent(object):
            __metaclass__ = EventMeta
            eid = ''
        self.assertEqual(TestEvent.tags, [''])

    def test_non_empty_eid(self):
        class TestEvent(object):
            __metaclass__ = EventMeta
            eid = 'TEST.EVENT.EID'
        self.assertEqual(TestEvent.tags, ['', 'TEST', 'TEST.EVENT',
                                          'TEST.EVENT.EID'])


event_tests = unittest.TestSuite()
loader = unittest.TestLoader()

event_tests.addTests(loader.loadTestsFromTestCase(EventMetaTestCase))

if __name__ == '__main__':
    # Run
    unittest.TextTestRunner(verbosity=2).run(event_tests)

