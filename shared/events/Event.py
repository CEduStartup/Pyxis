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
            for piece in cls.eid.split('.')[:-1]:
                tag = '%s%s.' % (tag, piece)
                cls.tags.append(tag)
        else:
            cls.tags = ['.']


class BaseEvent:

    """ Base class for all events.

    Don't invoke this event.
    """

    __metaclass__ = EventMeta

    eid = '.'
    fire_time = None
    message = None
    logged = None
    log_level = None

class TrackerEvent(BaseEvent):

    """ Base class for all tracker events.

    Don't invoke this event.
    """

    eid = '.TRACKER.'
    tracker_id = None


class TrackerSuccessEvent(TrackerEvent):

    """ Invoked when tracker succesfully grabbed data.
    """

    eid = '.TRACKER.SUCCESS.'
    message = 'Tracker %s succesfully grabbed data.'


class TrackerFailureEvent(TrackerEvent):

    """ Base class for all tracker failures events.
    """

    eid = '.TRACKER.FAILURE.'


class TrackerParseErrorEvent(TrackerFailureEvent):

    """ Invoked when parser error occure during data grabbing.
    """

    eid = '.TRACKER.FAILURE.PARSE.'
    message = ''


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """

    eid = '.TRACKER.WORKFLOW.'

