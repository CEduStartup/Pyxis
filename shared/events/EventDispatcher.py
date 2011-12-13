""" This module contains event dispatcher for non-multithread components.

Usage example:

dispatcher = EventDispatcher(host, port, 'consumer')

dispatcher.subscribe([TrackerSuccessEvent], some_func_1)
dispatcher.subscribe([TrackerFailureEvent], some_func_2)
dispatcher.subscribe([TrackerSuccessEvent, TrackerFailureEvent], some_func_3)

dispatcher.dispatch()
"""

from shared.events.EventManager import EventReceiver
from shared.Utils import get_base_classes


class EventDispatcher(object):

    """ Dispatches events to multiple consumers.
    This class is non thread safe.
    """

    def __init__(self, server_host, server_port, tubes):
        if not isinstance(tubes, tuple):
            raise RuntimeError('"tubes" parameter must be tuple or list')

        self._receiver = EventReceiver(server_host, server_port, tubes,
                                       self._dispatch_event)
        self._subscriptions = {}

    def _dispatch_event(self, event):
        events = get_base_classes(event.__class__)
        for event_cls in events:
            for subscription in self._subscriptions.get(event_cls, []):
                subscription(event)

    def dispatch(self):
        self._receiver.dispatch()

    def subscribe(self, events, callback):
        """ Subscribes for bunch of events. Receiving of events arranged by
        using returned id in receive method.

        :Parameters:
            - `events` a list of event EIDs.
            - `callback`: a callable object which accepts an instance of event
              as argument.
        """
        # Subscribe given callback for certain events or event types.
        for event in events:
            if event in self._subscriptions:
                self._subscriptions[event].append(callback)
            else:
                self._subscriptions[event] = [callback]

