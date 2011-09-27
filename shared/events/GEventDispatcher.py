from gevent.queue import Queue

from EventDispatcher import EventDispatcher


class GEventDispatcher(EventDispatcher):

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

    def receive(self, subscriber_id):
        return self._subscribers[subscriber_id].get()

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

