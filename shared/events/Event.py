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

    """ Metaclass for event classes. Used for putting tags into class field.
    These tags are defining topics to subscribe when listening for events.
    """

    def __init__(cls, name, bases, dct):
        super(EventMeta, cls).__init__(name, bases, dct)
        cls.tags = ['']
        if cls.eid:
            tag_parts = cls.eid.split('.')
            tag = tag_parts[0]
            cls.tags.append(tag)
            for part in tag_parts[1:]:
                tag = '%s.%s' % (tag, part)
                cls.tags.append(tag)


class BaseEvent:

    """ Base class for all events.
    Don't invoke this event.

    :Class variables:
        - `eid`: string event id.
        - `time`: float. The time of event creation.
        - `msg`: If this is a loggable event than this field should contain
          a log message text.
        - `log_level`: INFO, DEBUG, etc.

        - `_serializeble_attrs`: this list contains all attributes of the event
          which will be serialized and deserialized.
        - `_msg_args`: please update with arguments needed for log message
          formating.
    """

    __metaclass__ = EventMeta

    eid = ''
    time = None
    # Log message text. For string formating please use dictionary
    # ('%(key_name)s'). You can pass all arguments to `__init__()` as a keyword
    # parameters.
    msg = None
    log_level = None

    _serializeble_attrs = ['eid', 'time']
    _msg_args = ['message']

    def __init__(self, custom_time=None, **kwargs):
        """Initialize event instance.

        :Parameters:
            - `custom_time`: float custom creation time. If it's not defined,
              then current time will be used.
            - `kwargs` can contain additional attributes for `msg` formating.
              *NOTE*: Please update `_msg_args` with `kwargs`.
        """
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
            if (attr not in self._serializeble_attrs and
                attr not in self._msg_args):

                del attributes[attr]

        return attributes

    def __setstate__(self, state):
        """Restore an object from serialized state.
        """
        # Log message formatting.
        msg_args = dict([(k, state[k]) for k in self._msg_args])
        if self.msg:
            self.msg = self.msg % msg_args

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


class TrackerEvent(BaseEvent):

    """ Base class for all tracker events.

    Don't invoke this event.
    """

    eid = 'TRACKER'
    tracker_id = None


class TrackerSuccessEvent(TrackerEvent):

    """ Invoked when tracker succesfully grabbed data.
    """

    eid = 'TRACKER.SUCCESS'
    msg = 'Tracker %s succesfully grabbed data.'


class TrackerFailureEvent(TrackerEvent):

    """ Base class for all tracker failures events.
    """

    eid = 'TRACKER.FAILURE'


class TrackerParseErrorEvent(TrackerFailureEvent):

    """ Invoked when parser error occure during data grabbing.
    """

    eid = 'TRACKER.FAILURE.PARSE'
    msg = ''


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """

    eid = 'TRACKER.WORKFLOW'


class LoggerEvent(BaseEvent):
    """ Base class for all logger events. """

    eid = 'LOGGER'
    msg = '%(message)s'

class LoggerInfoEvent(LoggerEvent):
    """ Event used for logger's info messages. """

    eid = 'LOGGER.INFO'


class LoggerWarningEvent(LoggerEvent):
    """ Event used for logger's warning messages. """

    eid = 'LOGGER.WARNING'


class LoggerDebugEvent(LoggerEvent):
    """ Event used for logger's debug messages. """

    eid = 'LOGGER.DEBUG'


class LoggerCriticalEvent(LoggerEvent):
    """ Event used for logger's critical messages. """

    eid = 'LOGGER.CRITICAL'


# Maps event EID to event class. You need to update this mapping each time you
# adding new event class.
_EID_EVENT_MAPPING = {
    TrackerSuccessEvent.eid: TrackerSuccessEvent,
    TrackerFailureEvent.eid: TrackerFailureEvent,
    TrackerParseErrorEvent.eid: TrackerParseErrorEvent,
    TrackerWorkflowEvent.eid: TrackerWorkflowEvent,

    LoggerInfoEvent.eid: LoggerInfoEvent,
    LoggerWarningEvent.eid: LoggerWarningEvent,
    LoggerDebugEvent.eid: LoggerDebugEvent,
    LoggerCriticalEvent.eid: LoggerCriticalEvent,
}

# Defines a list of suitable tubes for each EID. You need to update this
_EID_TUBE_MAPPING = {
    TrackerSuccessEvent.eid: (LOGGER_TUBE,),
    TrackerFailureEvent.eid: (LOGGER_TUBE,),
    TrackerParseErrorEvent.eid: (LOGGER_TUBE,),
    TrackerWorkflowEvent.eid: (LOGGER_TUBE,),

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

