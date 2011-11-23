""" Intercomponent events definitions.
"""

import pickle
import time

from config.mq import LOGGER_TUBE, COLLECTOR_TUBE


class EventError(Exception):

    """Base class for all events error.
    """


class EventSerializationError(EventError):

    """This exception indicates that an event serialization has been failed.
    """


class NoSuchEventError(EventError):

    """Indicates that event whth given EID doesn't exist.
    """


class EventMeta(type):

    """Metaclass for event classes. Used for putting tags into class field.
    These tags are defining topics to subscribe when listening for events.
    """

    def __init__(mcs, name, bases, dct):
        super(EventMeta, mcs).__init__(name, bases, dct)
        mcs.tags = ['']
        if mcs.eid:
            tag_parts = mcs.eid.split('.')
            tag = tag_parts[0]
            mcs.tags.append(tag)
            for part in tag_parts[1:]:
                tag = '%s.%s' % (tag, part)
                mcs.tags.append(tag)


class BaseEvent:

    """ Base class for all events.
    Don't invoke this event.

    :Class variables:
        - `eid`: string event id.
        - `time`: float. The time of event creation.
        - `level`: INFO, DEBUG, etc.
        - `REQUIRED_ATTRS`: this attributes must allways be passed as kwargs
          when firing the events.
          
    Arguments, which starts with _ or uppercase, will not be serialized
    """

    __metaclass__ = EventMeta

    eid = None
    time = None
    level = None

    REQUIRED_ATTRS = []

    def __init__(self, custom_time=None, **kwargs):
        """Initialize event instance.

        :Parameters:
            - `custom_time`: float custom creation time. If it's not defined,
              then current time will be used.
            - `kwargs` can contain additional attributes for `msg` formating.
        """
        self.check_required_attrs(kwargs)
        self.__dict__.update(kwargs)
        self._set_fire_time(custom_time=custom_time)

    def __getstate__(self):
        """This method will be invoked by `serialize()`. Its purpose is to
        return only valuable attributes of the events which should be
        serialized.
        """
        attributes = self.__dict__.copy()
        for attr in self.__dict__:
            # Delete all attributes which cannot be serialized.
            if attr.startswith('_') or attr.istitle():
                del attributes[attr]

        return attributes

    def __setstate__(self, state):
        """Restore an object from serialized state.
        """
        self.__dict__.update(state)

    def check_required_attrs(self, args):
        """Check if all required attributes are present in kwargs dict.
        """
        for attr in self.REQUIRED_ATTRS:
            if not attr in args:
                raise EventError('Required attribute "%s" is not specified.' %
                                    (attr,))

    def _set_fire_time(self, custom_time=None):
        """Set the event creation time.

        :Parameters:
            - `custom_time`: float. Custom creation time. In case when it's not
              `None` then set creation time to `custom_time`, otherwise set
              creation time to `time.time()`.
        """
        self.time = custom_time or time.time()

    def serialize(self):
        """Serialize an event object to string.

        :Return:
            - pickle representation of event.
        """
        try:
            return pickle.dumps(self)
        except pickle.PicklingError, err:
            raise EventSerializationError(str(err))


class BaseLogEvent(BaseEvent):

    """Base class for all events which should be logged.
    New instance attributes::

        - `msg`: If this is a loggable event than this field should contain
          a log message text.
    """

    # Log message text. For string formating please use dictionary
    # ('%(key_name)s'). You can pass all arguments to `__init__()` as a keyword
    # parameters.
    msg = None
    
    def format_message(self):
        """Returns formatted message."""
        return self.msg % self.__dict__



# Collector events.

class CollectorEvent(BaseLogEvent):

    """Base class for all collector events.
    """

    eid = 'COLLECTOR'
    level = 'info'


class CollectorSuccessEvent(CollectorEvent):

    """Base class for all tracker success events.
    """

    eid = 'COLLECTOR.SUCCESS'
    level = 'info'


class CollectorFailureEvent(CollectorEvent):

    """Base class for all collector failure events.
    """

    REQUIRED_ATTRS = ['error_details']

    eid = 'COLLECTOR.FAILURE'
    level = 'crit'
    msg = 'Collector critical error. Details: %(error_details)s'


class CollectorServiceStartedEvent(CollectorSuccessEvent):

    """Indicates that collector successfully started a service.
    """

    REQUIRED_ATTRS = ['srv_name']

    eid = 'COLLECTOR.SERVICE_STARTED.SUCCESS'
    msg = 'Service "%(srv_name)s" started succesfully.'


# Tracker events.

class TrackerEvent(BaseLogEvent):

    """Base class for all tracker events.

    Don't invoke this event.
    """

    eid = 'TRACKER'
    tracker_id = None


class TrackerSuccessEvent(TrackerEvent):

    """Base class for all tracker success events.
    """

    eid = 'TRACKER.SUCCESS'
    level = 'info'


class TrackerFailureEvent(TrackerEvent):

    """Base class for all tracker failure events.
    """

    REQUIRED_ATTRS = ['tracker_id', 'error_details']

    eid = 'TRACKER.FAILURE'
    level = 'crit'
    msg = """\
Tracker "%(tracker_id)s" unhandled error. Details: %(error_details)s"""


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """

    eid = 'TRACKER.WORKFLOW'


class TrackerGrabSuccessEvent(TrackerSuccessEvent):

    """Invoked when tracker successfully grabbed data.
    """

    REQUIRED_ATTRS = ['tracker_id']

    eid = 'TRACKER.GRAB.SUCCESS'
    msg = 'Tracker %(tracker_id)s successfully grabbed data.'


class TrackerGrabFailureEvent(TrackerFailureEvent):

    """Tracker cannot grab data due to some problem.
    """

    REQUIRED_ATTRS = ['tracker_id', 'error_details']

    eid = 'TRACKER.GRAB.FAILURE'
    msg = 'Tracker %(tracker_id)s cannot grab data. Details: '\
          '%(error_details)s'


class TrackerParseErrorEvent(TrackerFailureEvent):

    """Invoked when parser error occured during data grabbing.
    """

    REQUIRED_ATTRS = ['tracker_id', 'data_type', 'error_details']

    eid = 'TRACKER.FAILURE.PARSE'
    msg = 'Tracker %(tracker_id)s unable to parse %(data_type)s data. '\
          'Details: %(error_details)s'


# Logger events.

class LoggerEvent(BaseLogEvent):

    """ Base class for all logger events. """

    REQUIRED_ATTRS = ['message']

    eid = 'LOGGER'
    msg = '%(message)s'
    level = 'gene'


class LoggerInfoEvent(LoggerEvent):
    """ Event used for logger's info messages. """

    eid = 'LOGGER.INFO'
    level = 'info'


class LoggerWarningEvent(LoggerEvent):
    """ Event used for logger's warning messages. """

    eid = 'LOGGER.WARNING'
    level = 'warn'


class LoggerDebugEvent(LoggerEvent):
    """ Event used for logger's debug messages. """

    eid = 'LOGGER.DEBUG'
    level = 'debg'


class LoggerCriticalEvent(LoggerEvent):
    """ Event used for logger's critical messages. """

    eid = 'LOGGER.CRITICAL'
    level = 'crit'


# Configuration changes events.

class TrackerConfigEvent(BaseLogEvent, BaseEvent):

    """Base class for all events which indicate about changes in tracker
    configuration.
    """

    REQUIRED_ATTRS = ['tracker_id']
    eid = 'CONFIG.TRACKER'
    msg = 'Tracker %(tracker_id)s configuration event.'
    level = 'info'


class NewTrackerAddedEvent(TrackerConfigEvent):

    """Indicates that new tracker was added and collector needs to read its
    configuration from relational DB and add this tracker to scheduler.
    """

    eid = 'CONFIG.TRACKER.ADDED'
    msg = 'Tracker %(tracker_id)s added.'


class TrackerConfigChangedEvent(TrackerConfigEvent):

    """Indicates that configuration of tracker with the given `tracker_id` was
    changed.
    """

    eid = 'CONFIG.TRACKER.CHANGED'
    msg = 'Tracker %(tracker_id)s was updated.'


class TrackerDeletedEvent(TrackerConfigEvent):

    """Indicates that tracker with the given `tracker_id` was deleted.
    """

    eid = 'CONFIG.TRACKER.DELETED'
    msg = 'Tracker %(tracker_id)s was deleted.'


# Maps event EID to event class. You need to update this mapping each time you
# adding new event class.
_EID_EVENT_MAPPING = {
    # Tracker config changes events.
    NewTrackerAddedEvent.eid: NewTrackerAddedEvent,
    TrackerConfigChangedEvent.eid: TrackerConfigChangedEvent,
    TrackerDeletedEvent.eid: TrackerDeletedEvent,

    # Collector events.
    CollectorServiceStartedEvent.eid: CollectorServiceStartedEvent,
    CollectorFailureEvent.eid: CollectorFailureEvent,

    # Tracker events.
    TrackerGrabSuccessEvent.eid: TrackerGrabSuccessEvent,
    TrackerGrabFailureEvent.eid: TrackerGrabFailureEvent,
    TrackerParseErrorEvent.eid: TrackerParseErrorEvent,
    TrackerWorkflowEvent.eid: TrackerWorkflowEvent,

    # Logger events.
    LoggerInfoEvent.eid: LoggerInfoEvent,
    LoggerWarningEvent.eid: LoggerWarningEvent,
    LoggerDebugEvent.eid: LoggerDebugEvent,
    LoggerCriticalEvent.eid: LoggerCriticalEvent,
}

# Defines a list of suitable tubes for each EID. You need to update this
_EID_TUBE_MAPPING = {
    # Tracker config changes events.
    NewTrackerAddedEvent.eid: (COLLECTOR_TUBE, LOGGER_TUBE),
    TrackerConfigChangedEvent.eid: (COLLECTOR_TUBE, LOGGER_TUBE),
    TrackerDeletedEvent.eid: (COLLECTOR_TUBE, LOGGER_TUBE),

    # Collector events.
    CollectorServiceStartedEvent.eid: (LOGGER_TUBE,),
    CollectorFailureEvent.eid: (LOGGER_TUBE,),

    # Tracker events.
    TrackerGrabSuccessEvent.eid: (LOGGER_TUBE,),
    TrackerGrabFailureEvent.eid: (LOGGER_TUBE,),
    TrackerParseErrorEvent.eid: (LOGGER_TUBE,),
    TrackerWorkflowEvent.eid: (LOGGER_TUBE,),

    # Logger events.
    LoggerInfoEvent.eid: (LOGGER_TUBE,),
    LoggerWarningEvent.eid: (LOGGER_TUBE,),
    LoggerDebugEvent.eid: (LOGGER_TUBE,),
    LoggerCriticalEvent.eid: (LOGGER_TUBE,),
}

def get_tubes(eid):
    """Return a list of tubes appropriate for given `eid`.

    :Exception:
        - `NoSuchEventError` in case when given `eid` was not found.
    """
    try:
        return _EID_TUBE_MAPPING[eid]
    except KeyError:
        raise NoSuchEventError(eid)

def get_event(eid):
    """Try to return an event class for given `eid`.

    Please *always* use this method to get event object.

    :Return:
        - event class.

    :Exception:
        - `NoSuchEventError` in case when event with such `eid` doesn't exists.
    """
    try:
        return _EID_EVENT_MAPPING[eid]
    except KeyError:
        raise NoSuchEventError(eid)

