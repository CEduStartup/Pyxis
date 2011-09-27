import unittest

from Scheduler import Scheduler
from trackers.Tracker import DummyTracker


class SchedulerTestCase(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()

    def test_add_tracker(self):
        tracker = DummyTracker(1, None)
        self.scheduler.add_tracker(tracker)

        self.assertEqual(self.scheduler.tasks.qsize(), 1)

    def test_remove_tracker(self):
        tracker = DummyTracker(1, None)
        self.scheduler.remove_tracker(tracker)

        self.assertEqual(len(self.scheduler.to_remove), 1)

    def test_get_run_queue_size(self):
        tracker = DummyTracker(1, None)
        self.scheduler.to_run.put(tracker)

        self.assertEqual(self.scheduler.to_run.qsize(), 1)


scheduler_tests = unittest.TestSuite()
loader = unittest.TestLoader()

scheduler_tests.addTests(loader.loadTestsFromTestCase(SchedulerTestCase))

