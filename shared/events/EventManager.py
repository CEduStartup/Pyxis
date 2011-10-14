"""This module contains event sender and receiver.
"""

import beanstalkc

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
        if tubes is not None:
            self.set_watching_tubes(tubes)

    def get_tubes(self):
        """Return a list of tubes which currently available.
        """
        return self._client.tubes()

## TODO: Move this to event receiver class.
##
##    def get_watching_tubes(self):
##        """Return a list of tubes which are in watchlist.
##        """
##        return self._client.watching()
##
##    def set_watching_tubes(self, tubes):
##        """Add tube(s) to watch list. All previous tubes will be removed.
##
##        :Parameters:
##            - `tubes` string which contain a name of tube to watch for (of a
##              list of strings).
##        """
##        current_tubes =set(self.get_watching_tubes())
##
##        if not isinstance(tubes, (list, tuple))
##            new_tubes = set([tubes,])
##        else:
##            new_tubes = set(tubes)
##
##        to_delete = current_tubes.difference(new_tubes)
##        to_add = new_tubes.difference(current_tubes)
##
##        for tube in to_delete:
##            self._client.ignore(t)
##
##        for tube in to_add:
##            self._client.watch(tube)


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

    def fire(event):
        """Put event into current tube.

        :Parameters:
            - `event`: an picklable object.
        """
        self._client.put(event)

