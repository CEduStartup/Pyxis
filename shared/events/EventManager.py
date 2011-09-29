"""This module contains event sender and receiver.
"""

import beanstalkc
import pickle
from shared.events.Event import BaseEvent

from shared.events import Event

# This constant probably should be moved to settings.py
# How long we can wait for information.
TIMEOUT = 3

class EventManagerBase(object):

    """Base class for event sender and event receiver.
    """

    def __init__(self, server_host='localhost', server_port=11300):
        """Initialize event manager.

        :Parameters:
            - `server_host`: string which contains hostname where the
              beanstalkd server located.
            - `server_port`: integer value of the port to connect to.
            - `tube`: string which contains a name of the tube.
        """
        self._client = beanstalkc.Connection(host=server_host, port=server_port)
        self._client.connect()

class EventSender(EventManagerBase):

    """Used to send event to different tubes.
    """

    def _create_event_obj(self, eid, **kwargs):
        """Create an event and pass all required arguments.

        :Parameters:
            - `eid`: event ID.
            - `kwargs`: additional arguments required for event.

        :Return:
            An event object.
        """
        # TODO: errors handling.
        event_cls = Event.get_event(eid)
        return event_cls(**kwargs)

    def _serialize_event(self, event):
        """Serialize an event to string using pickle module.
        """
        return event.serialize()

    def fire(self, event, tubes=None, **kwargs):
        """Put event into current tube.

        :Parameters:
            - `event`: an event id.
            - `tubes`: a list of tubes to send the `event` to.
            - `kwargs`: dictionary which contains all required parameters to
              format log message.
        """
        event = self._create_event_obj(event, **kwargs)
        serialized_event = self._serialize_event(event)

        if tubes is not None:
            destanation = tubes
        else:
            destanation = Event.get_tubes(event.eid)

        # TODO: errors handling.
        for tube in destanation:
            self._client.use(tube)
            self._client.put(serialized_event)

def null_callback(event):
    """Null event handler.
    """
    pass

class EventReceiver(EventManagerBase):

    """ Used to receive messages from a single tube.
    This class is non thread safe.
    """

    def __init__(self, server_host='localhost', server_port=11300,
                 tubes=('default',), callback=null_callback):
        EventManagerBase.__init__(self, server_host, server_port)
        self._callback = callback
        self._tubes = tubes

    def _subscribe(self):
        """Set tubes to watch for.
        """
        currect = self._client.ignore('default')
        for tube in self._tubes:
            self._client.watch(tube)

    def dispatch(self):
        """ Method that receive from message queue, restore and throw events to
        subscribed callback.
        """
        self._subscribe()

        while True:
            # TODO: error handling
            try:
                job = self._client.reserve()
                event = pickle.loads(job.body)
                self._callback(event)
            finally:
                job.delete()

