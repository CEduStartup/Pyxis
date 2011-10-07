""" Intercomponent events definitions.
"""

import pickle
import time


LOGGER_TUBE = 'LOGGER_TUBE'

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
        - `msg`: If this is a loggable event than this field should contain
          a log message text.
        - `level`: INFO, DEBUG, etc.

        - `_serializeble_attrs`: this list contains all attributes of the event
          which will be serialized and deserialized.
    """

    __metaclass__ = EventMeta

    eid = None
    time = None
    # Log message text. For string formating please use dictionary
    # ('%(key_name)s'). You can pass all arguments to `__init__()` as a keyword
    # parameters.
    msg = None
    level = None

    _serializeble_attrs = ['time', 'tags']

    def __init__(self, custom_time=None, **kwargs):
        """Initialize event instance.

        :Parameters:
            - `custom_time`: float custom creation time. If it's not defined,
              then current time will be used.
            - `kwargs` can contain additional attributes for `msg` formating.
        """
        self.__dict__.update(kwargs)
        self._set_fire_time(custom_time=custom_time)
        # Preserve all additional arguments passed to event constructor.
        self._serializeble_attrs.extend(kwargs.keys())

    def __getstate__(self):
        """This method will be invoked by `serialize()`. Its purpose is to
        return only valuable attributes of the events which should be
        serialized.
        """
        attributes = self.__dict__.copy()
        for attr in self.__dict__:
            # Delete all attributes which cannot be serialized.
            if attr not in self._serializeble_attrs:
                del attributes[attr]

        return attributes

    def __setstate__(self, state):
        """Restore an object from serialized state.
        """
        # Log message formatting.
        if self.msg:
            self.msg = self.msg % state

        self.__dict__.update(state)

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
        except pickle.PicklingError, e:
            raise EventSerializationError(str(e))


# Collector events.

class CollectorEvent(BaseEvent):

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

    eid = 'COLLECTOR.FAILURE'
    level = 'crit'
    msg = 'Collector critical error. Details: %(error_details)s'


class CollectorServiceStartedEvent(CollectorSuccessEvent):

    """Indicates that collector successfully started a service.
    """

    eid = 'COLLECTOR.SERVICE_STARTED.SUCCESS'
    msg = 'Service "%(srv_name)s" started succesfully.'

# Tracker events.

class TrackerEvent(BaseEvent):

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

    eid = 'TRACKER.FAILURE'
    level = 'crit'


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """

    eid = 'TRACKER.WORKFLOW'


class TrackerGrabSuccessEvent(TrackerSuccessEvent):

    """Invoked when tracker successfully grabbed data.
    """

    eid = 'TRACKER.GRAB.SUCCESS'
    msg = 'Tracker %(tracker_id)s successfully grabbed data.'


class TrackerGrabFailureEvent(TrackerFailureEvent):

    """Tracker cannot grab data due to some problem.
    """

    eid = 'TRACKER.GRAB.FAILURE'
    msg = 'Tracker %(tracker_id)s cannot grab data. Details: '\
          '%(error_details)s'


class TrackerParseErrorEvent(TrackerFailureEvent):

    """Invoked when parser error occured during data grabbing.
    """

    eid = 'TRACKER.FAILURE.PARSE'
    msg = 'Tracker %(tracker_id)s unable to parse %(data_type)s data. '\
          'Details: %(error_details)s'


# Logger events.

class LoggerEvent(BaseEvent):
    """ Base class for all logger events. """

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

# Maps event EID to event class. You need to update this mapping each time you
# adding new event class.
_EID_EVENT_MAPPING = {
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

