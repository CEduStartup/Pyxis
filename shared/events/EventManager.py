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
        
        #if tubes is not None:
        #    self.set_watching_tubes(tubes)

    def get_tubes(self):
        """Return a list of tubes which currently available.
        """
        return self._client.tubes()


class EventSender(EventManagerBase):

    """Used to send event to different tubes.
    """

    def get_current_tube(self):
        """Return a tube which is currently in use (to put event to).
        """
        return self._client.using()

    def set_current_tube(self, tube):
        """Set a tube to put event to.

        :Parameters:
            - `tube`: string name of the tube.
        """
        if not tube in self.get_tubes():
            # TODO: we need to handle this situation correctly.
            pass
        self._client.using(tube)

    def fire(self, event):
        """Put event into current tube.

        :Parameters:
            - `event`: an picklable object.
        """
        self._client.put(pickle.dumps(event))


class EventReceiver(EventManagerBase):

    """ Used to receive messages from a single tube.
    This class is non thread safe.
    """

    def __init__(self, server_host, server_port, tube, callback):
        EventManagerBase.__init__(self, server_host, server_port, tube)
        self._callback = callback

    def dispatch(self):
        """ Method that receive from message queue, restore and throw events to
        subscribed callback.
        """

        while True:
            # TODO: error handling
            try:
                job = self._client.reserve()
                event = pickle.loads(job.body)
                self._callback(event)
            finally:
                job.delete()

