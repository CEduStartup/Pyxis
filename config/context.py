"""This module containts class and instance of run context. It is used by
shared modules to identify itselves in different system components.
"""

class RunContext(object):
    """Class for keeping running context.
    """

    component_name = None

    def __init__(self, component_name):
        self.component_name = component_name

def create_context(component_name):
    """Function that creates run context by given component name.

    :Parameters:
        - `component_name`: string for name of the component.
    """
    global context
    context = RunContext(component_name)

context = None

