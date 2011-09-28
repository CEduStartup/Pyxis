"""This module contains event sender and receiver.
"""

import beanstalkc
import pickle

# This constant probably should be moved to settings.py
# How long we can wait for information.
TIMEOUT = 3

class EventManagerBase(object):

    """Base class for event sender and event receiver.
    """

    def __init__(self, server_host, server_port, tubes=None):
        """Initialize event manager.

        :Parameters:
            - `server_host`: string which contains hostname where the
              beanstalkd server located.
            - `server_port`: integer value of the port to connect to.
            - `tube`: string which contains a name of the tube.
        """
        self._client = beanstalkc.Connection(host=server_host, port=server_port)
        self._client.connect()

    def get_tubes(self):
        """Return a list of tubes which currently available.
        """
        return self._client.tubes()


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
        # Here we need to create an appropriate event object using it's eid.

    def _serialize_event(self, event):
        """Serialize an event to string using pickle module.
        """
        return event.serialize()

    def fire(event, tubes=None, **kwargs):
        """Put event into current tube.

        :Parameters:
            - `event`: an event id.
            - `tubes`: a list of tubes to send the `event` to.
            - `kwargs`: dictionary which contains all required parameters to
              format log message.
        """
        event = self._create_event_obj(event, **kwargs)
        serialized_event = self._serialize_event(event)

        # We need to determine in which tube we should send an event.


class EventReceiver(EventManagerBase):

    """ Used to receive messages from a single tube.
    This class is non thread safe.
    """

    def __init__(self, server_host, server_port, tube, callback):
        EventReceiverBase.__init__(self, server_host, server_port, tube)
        self._callback = callback

    def dispatch(self):
        """ Method that receive from message queue, restore and throw events to
        subscribed callback.
        """

        while True:
            # TODO: error handling
            job = self._client.reserve()
            event = pickle.loads(job.body)
            job.delete()
            self._callback(event)

