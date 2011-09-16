"""This module contains lxml compatible targets which can correctly work with
gevent.
"""

import gevent

from lxml import etree

# How many elements will be parsed before `gevent.sleep()` fired.
ELEMENTS_IN_ROUND = 100

class geventTreeBuilder(etree.TreeBuilder):

    """This class do the same work as `etree.TreeBuilder` but it's compatible
    with gevent.
    """

    def __init__(self, max_elements=ELEMENTS_IN_ROUND):
        etree.TreeBuilder.__init__(self)
        self._elements_in_round = max_elements
        self._elements_parsed = 0

    def start(self, tag, attrs):
        if self._elements_parsed == self._elements_in_round:
            self._elements_in_round = 0
            gevent.sleep(0)

        return etree.TreeBuilder.start(self, tag, attrs)

