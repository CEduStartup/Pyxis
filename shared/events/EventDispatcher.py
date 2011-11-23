""" This module contains event dispatcher for non-multithread components.

Usage example:

dispatcher = EventDispatcher(host, port, 'consumer')

dispatcher.subscribe([TrackerSuccessEvent], some_func_1)
dispatcher.subscribe([TrackerFailureEvent], some_func_2)
dispatcher.subscribe([TrackerSuccessEvent, TrackerFailureEvent], some_func_3)

dispatcher.dispatch()
"""

from shared.events.Event import get_event
from shared.events.EventManager import EventReceiver


class EventDispatcher(object):

    """ Dispatches events to multiple consumers.
    This class is non thread safe.
    """

    def __init__(self, server_host, server_port, tag):
        self._receiver = EventReceiver(server_host, server_port, tag,
                                       self._dispatch_event)
        self._subscriptions = {}

    def _dispatch_event(self, event):
        for tag in event.tags:
            for subscription in self._subscriptions[tag]:
                subscription(event)

    def _get_tags_compressed(self, tags):
        """ Reduces tags list to the least effective according to
        event-subevent relations.
        """
        compressed = []
        for tag in tags:
            for key, value in enumerate(compressed):
                if self._is_subtag(value, tag):
                    compressed[key] = tag
                    break
                if self._is_subtag(tag, value):
                    break
            else:
                compressed.append(tag)
        return compressed

    def _get_tags(self, events):
        """ Creates tags list based on given events list.
        """
        tags = []
        for event in events:
            tags.append(event.tags[-1])
        return self._get_tags_compressed(tags)

    def _is_subtag(self, subtag, tag):
        """ Checks whether tag-subtag relation satisfied.
        """

        return tag.startswith(subtag)

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
        # Convert a list of EIDs to list of event class instances.
        event_objects = [get_event(e) for e in events]

        # Subscribe given callback for certain events or event types.
        subscriber_tags = self._get_tags(event_objects)
        for tag in subscriber_tags:
            if not tag in self._subscriptions:
                self._subscriptions[tag] = []
            self._subscriptions[tag].append(callback)

