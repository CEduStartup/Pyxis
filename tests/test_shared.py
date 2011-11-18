""" Unit test module that collects all unittest suites from shared and root
test suites from shared submodules.
"""

import unittest

from test_shared_events import events_tests


shared_tests = unittest.TestSuite()

# Collect test suites
shared_tests.addTests(events_tests)

if __name__ == '__main__':
    # Run
    unittest.TextTestRunner(verbosity=2).run(shared_tests)

