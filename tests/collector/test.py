""" Unit test module that collects all unittest suites from collector and root
test suites from collector submodules.
"""

import unittest

from test_scheduler import scheduler_tests


collector_tests = unittest.TestSuite()

# Collect test suites
collector_tests.addTests(scheduler_tests)

