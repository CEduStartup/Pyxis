""" This module contains event dispatcher for multithread components which use
gevent.


Usage example:

dispatcher = EventDispatcher(host, port, 'consumer')

# Subscribe with callback
dispatcher.subscribe([TrackerEvent], some_func_1)
# Subscribe without callback
tracker_finished_subscr = dispatcher.subscribe([TrackerSuccessEvent, TrackerFailureEvent])

# Subscriptions with callback are handled in dispatcher main loop.
gevent.spawn(dispatcher.dispatch)

# Handling subscription without callback
while True:
    # do something
    timeout = time_left_to_next_action
    event = dispatcher.receive(tracker_finished_subscr, timeout)
"""

from gevent.queue import Queue

from .EventDispatcher import EventDispatcher


class GEventDispatcher(EventDispatcher):

    """ Dispatches events to multiple consumers.

    Allows to subscribe without callback. In that case subscriber should
    intentionally receive events.

    This class is thread safe.
    """

    def __init__(self, server_host, server_port, tag):
        EventDispatcher.__init__(self, server_host, server_port, tag)
        self._subscribers = []

    def _dispatch_event(self, event):
        for tag in event.tags:
            for listener in self._listeners[tag]:
                if isinstance(listener, Queue):
                    listener.put(event)
                else:
                    listener(event)

    def receive(self, subscriber_id, timeout=None):
        return self._subscribers[subscriber_id].get(timeout=timeout)

    def subscribe(self, events, callback=None):
        """ Subscribes for bunch of events. Receiving of events arranged by
        using returned id in receive method.
        """

        if callback == None:
            callback = Queue()

        EventDispatcher.subscribe(self, events, callback)

        subscriber_id = len(self._subscribers)
        self._subscribers.append(queue)

        return subscriber_id

