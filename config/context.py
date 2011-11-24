"""This module containts class and instance of run context. It is used by
shared modules to identify itselves in different system components.
"""

class RunContext(object):
    """Class for keeping running context.
    """

    component_name = None

    def __init__(self, component_name):
        self.component_name = component_name

context = None

