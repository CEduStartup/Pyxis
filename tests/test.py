""" Main test module. In this module are collecting only highest level test
suites from each component tests.
"""

import unittest

from collector.test import collector_tests


# Init
all_tests = unittest.TestSuite()

# Collect tests
all_tests.addTests(collector_tests)

# Run
unittest.TextTestRunner(verbosity=2).run(all_tests)

