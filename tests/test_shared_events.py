""" Unit test module that collects all unittest suites from events and root
test suites from events submodules.
"""

import unittest

from test_shared_events_event import event_tests


events_tests = unittest.TestSuite()

# Collect test suites
events_tests.addTests(event_tests)

if __name__ == '__main__':
    # Run
    unittest.TextTestRunner(verbosity=2).run(events_tests)

