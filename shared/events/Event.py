""" Intercomponent events definitions.
"""


class EventMeta(type):

    """ Metaclass for event classes. Used for putting tags into class field.
    These tags are defining topics to subscribe when listening for events.
    """

    def __init__(cls, name, bases, dct):
        super(EventMeta, cls).__init__(name, bases, dct)
        if cls.eid:
            cls.tags = []
            tag = ''
            for piece in cls.eid.split('.'):
                tag = '%s.%s' % (tag, piece)
                cls.tags.append(tag)
        else:
            cls.tags = ['.']


class BaseEvent:

    """ Base class for all events.

    Don't invoke this event.
    """

    __metaclass__ = EventMeta

    eid = None
    fire_time = None
    message = None
    logged = None
    log_level = None

