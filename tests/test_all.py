""" Main test module. In this module are collecting only highest level test
suites from each component tests.
"""

import unittest

from test_collector import collector_tests
from test_shared import shared_tests


# Init
all_tests = unittest.TestSuite()

# Collect tests
all_tests.addTests(collector_tests)
all_tests.addTests(shared_tests)

if __name__ == '__main__':
    # Run
    unittest.TextTestRunner(verbosity=2).run(all_tests)

