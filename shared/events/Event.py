""" Intercomponent events definitions.
"""

import pickle
import time

from config.context import context
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


class BaseEvent(object):

    """ Base class for all events.
    Don't invoke this event.

    :Class variables:
        - `time`: float. The time of event creation.
        - `level`: INFO, DEBUG, etc.
        - `REQUIRED_ATTRS`: this attributes must allways be passed as kwargs
          when firing the events.

    Arguments, which starts with _ or uppercase, will not be serialized
    """

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
    component = None

    def __init__(self, custom_time=None, **kwargs):
        super(BaseLogEvent, self).__init__(custom_time, **kwargs)

        self.component = context.component_name

    def format_message(self):
        """Returns formatted message."""
        return self.msg % self.__dict__



# Collector events.

class CollectorEvent(BaseLogEvent):

    """Base class for all collector events.
    """

    level = 'info'


class CollectorSuccessEvent(CollectorEvent):

    """Base class for all tracker success events.
    """

    level = 'info'


class CollectorFailureEvent(CollectorEvent):

    """Base class for all collector failure events.
    """

    REQUIRED_ATTRS = ['error_details']

    level = 'crit'
    msg = 'Collector critical error. Details: %(error_details)s'


class CollectorServiceStartedEvent(CollectorSuccessEvent):

    """Indicates that collector successfully started a service.
    """

    REQUIRED_ATTRS = ['srv_name']

    msg = 'Service "%(srv_name)s" started succesfully.'


# Tracker events.

class TrackerEvent(BaseLogEvent):

    """Base class for all tracker events.

    Don't invoke this event.
    """

    tracker_id = None


class TrackerSuccessEvent(TrackerEvent):

    """Base class for all tracker success events.
    """

    level = 'info'


class TrackerFailureEvent(TrackerEvent):

    """Base class for all tracker failure events.
    """

    REQUIRED_ATTRS = ['tracker_id', 'error_details']

    level = 'crit'
    msg = """\
Tracker "%(tracker_id)s" unhandled error. Details: %(error_details)s"""


class TrackerWorkflowEvent(TrackerEvent):

    """ Base class for all non-failure events during data grabbing.
    """



class TrackerGrabSuccessEvent(TrackerSuccessEvent):

    """Invoked when tracker successfully grabbed data.
    """

    REQUIRED_ATTRS = ['tracker_id']

    msg = 'Tracker %(tracker_id)s successfully grabbed data.'


class TrackerGrabFailureEvent(TrackerFailureEvent):

    """Tracker cannot grab data due to some problem.
    """

    REQUIRED_ATTRS = ['tracker_id', 'error_details']

    msg = 'Tracker %(tracker_id)s cannot grab data. Details: '\
          '%(error_details)s'


class TrackerParseErrorEvent(TrackerFailureEvent):

    """Invoked when parser error occured during data grabbing.
    """

    REQUIRED_ATTRS = ['tracker_id', 'data_type', 'error_details']

    msg = 'Tracker %(tracker_id)s unable to parse %(data_type)s data. '\
          'Details: %(error_details)s'


# Logger events.

class LoggerEvent(BaseLogEvent):

    """ Base class for all logger events. """

    REQUIRED_ATTRS = ['message']

    msg = '%(message)s'
    level = 'gene'


class LoggerInfoEvent(LoggerEvent):
    """ Event used for logger's info messages. """

    level = 'info'


class LoggerWarningEvent(LoggerEvent):
    """ Event used for logger's warning messages. """

    level = 'warn'


class LoggerDebugEvent(LoggerEvent):
    """ Event used for logger's debug messages. """

    level = 'debg'


class LoggerCriticalEvent(LoggerEvent):
    """ Event used for logger's critical messages. """

    level = 'crit'


# Configuration changes events.

class TrackerConfigEvent(BaseLogEvent, BaseEvent):

    """Base class for all events which indicate about changes in tracker
    configuration.
    """

    REQUIRED_ATTRS = ['tracker_id']
    msg = 'Tracker %(tracker_id)s configuration event.'
    level = 'info'


class NewTrackerAddedEvent(TrackerConfigEvent):

    """Indicates that new tracker was added and collector needs to read its
    configuration from relational DB and add this tracker to scheduler.
    """

    msg = 'Tracker %(tracker_id)s added.'


class TrackerConfigChangedEvent(TrackerConfigEvent):

    """Indicates that configuration of tracker with the given `tracker_id` was
    changed.
    """

    msg = 'Tracker %(tracker_id)s was updated.'


class TrackerDeletedEvent(TrackerConfigEvent):

    """Indicates that tracker with the given `tracker_id` was deleted.
    """

    msg = 'Tracker %(tracker_id)s was deleted.'


# Defines a list of suitable tubes for each EID. You need to update this
_EVENT_TUBE_MAPPING = {
    # Tracker config changes events.
    NewTrackerAddedEvent: (COLLECTOR_TUBE, LOGGER_TUBE),
    TrackerConfigChangedEvent: (COLLECTOR_TUBE, LOGGER_TUBE),
    TrackerDeletedEvent: (COLLECTOR_TUBE, LOGGER_TUBE),

    # Collector events.
    CollectorServiceStartedEvent: (LOGGER_TUBE,),
    CollectorFailureEvent: (LOGGER_TUBE,),

    # Tracker events.
    TrackerGrabSuccessEvent: (LOGGER_TUBE,),
    TrackerGrabFailureEvent: (LOGGER_TUBE,),
    TrackerParseErrorEvent: (LOGGER_TUBE,),
    TrackerWorkflowEvent: (LOGGER_TUBE,),

    # Logger events.
    LoggerInfoEvent: (LOGGER_TUBE,),
    LoggerWarningEvent: (LOGGER_TUBE,),
    LoggerDebugEvent: (LOGGER_TUBE,),
    LoggerCriticalEvent: (LOGGER_TUBE,),
}

def get_tubes(event_cls):
    """Return a list of tubes appropriate for given `eid`.

    :Exception:
        - `NoSuchEventError` in case when given `eid` was not found.
    """
    try:
        return _EVENT_TUBE_MAPPING[event_cls]
    except KeyError:
        raise NoSuchEventError(event_cls)

