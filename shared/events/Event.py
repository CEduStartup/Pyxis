""" Intercomponent events definitions.
"""

import pickle


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
        - `loggable`: bollean. Whether this event should be logged.
        - `log_level`: INFO, DEBUG, etc.

        - `_serializeble_attrs`: this list contains all attributes of the event
          which will be serialized and deserialized.
    """

    eid = None
    time = None
    msg = None
    loggable = None
    log_level = None

    _serializeble_attrs = ['eid', 'time', 'msg', 'loggable', 'log_level']

    def __getstate__(self):
        """This method will be invoked by `serialize()`. Its purpose is to
        return only valuable attributes of the events which should be
        serialized.
        """
        attributes = self.__dict__.copy()
        for attr in attributes:
            if attr not in self._serializeble_attrs:
                del attributes[attr]

        return attributes

    def __setstate__(self, state):
        """Restore an object from serialized state.
        """
        self.__dict__.update(state)

    def serialize(self):
        """Serialize and event object to string.

        :Return:
            - pickle representation of event.
        """
        try:
            return pickle.dumps(self)
        except pickel.PicklingError, e:
            raise EventSerializationError(str(e))

