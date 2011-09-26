import beanstalkc
import gevent

from gevent.queue import Queue


class EventReceiver(EventManagerBase):

    def __init__(self, server_host, server_port):
        super(EventReceiver, self).__init__(server_host, server_port)
        self._listeners = {}
        self._queues = []

    def _dispatch(self):
        """ This method implements main loop for dispatching events among
        subscribers.
        """

        while True:
            job = self._client.reserve()
            event = self._get_event(job.body)
            job.delete()
            for tag in event.tags:
                if tag in self._listeners:
                    for queue in self.listeners[tag]:
                        queue.put(event)
            gevent.sleep(0)

    def _get_event(self, raw_message):
        """ Creates event from raw message data.
        """
        pass

    def _get_tubes_compressed(self, tubes):
        """ Reduces tubes list to the least effective according to
        event-subevent relations.
        """

        compressed = []
        for tube in tubes:
            for i in xrange(len(compressed)):
                if self._is_subtube(compressed[i], tube):
                    compressed[i] = tube
                    break
                if self._is_subtube(tube, compressed[i]):
                    break
        return compressed

    def _get_tubes(self, events):
        """ Creates tubes list based on given events list.
        """

        tubes = []
        for event in events:
            tubes.append(event.tags[-1])
        return self._get_tubes_compressed(tubes)

    def _is_subtube(self, subtube, tube):
        """ Checks whether tube-subtube relation satisfied.
        """

        return tube.startswith(subtube)

    def receive(self, subscriber_id):
        return self._queues[subscriber_id].get()

    def start(self):
        gevent.spawn(self._dispatch)

    def subscribe(self, events):
        """ Subscribes for bunch of events. Receiving of events arranged by
        using returned id in receive method.
        """

        subscriber_id = len(self._queues)

        # Create separate queue for subscriber to dispatch events into it.
        queue = Queue()
        self._queues.append(queue)

        # Subscribe created queue for certain events or event types.
        subscriber_tubes = self._get_tubes(events)
        for tube in subscriber_tubes:
            self._listeners.get(tube, []).append(queue)

        # Update message queue to listen tubes for events just subscribed for.
        map(self._client.watch, subscriber_tubes)

        return subscriber_id

