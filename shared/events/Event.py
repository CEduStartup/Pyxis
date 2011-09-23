""" Intercomponent events definitions.
"""


class BaseEvent:

    """ Base class for all events.

    Don't invoke this event.
    """

    eid = None

    fire_time = None

    message = None

    logged = None

    log_level = None

