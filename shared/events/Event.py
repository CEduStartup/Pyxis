""" Intercomponent events definitions.
"""

import pickle
import time


class EventError(Exception):

    """Base class for all events error.
    """

class EventSerializationError(EventError):

    """This exception indicates that an event serialization has been failed.
    """

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

    eid = None
    time = None
    # Log message text. For string formating please use dictionary
    # ('%(key_name)s'). You can pass all arguments to `__init__()` as a keyword
    # parameters.
    msg = None
    log_level = None

    _serializeble_attrs = ['eid', 'time']
    _msg_args = []

    def __init__(self, custom_time=None, **kwargs):
        """Initialize event instance.

        :Parameters:
            - `custom_time`: float custom creation time. If it's not defined,
              then current time will be used.
            - `kwargs` can contain additional attributes for `msg` formating.
              *NOTE*: Please update `_msg_args` with `kwargs`.
        """
        self.__dict__.update(kwargs)
        self._set_fire_time()

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

