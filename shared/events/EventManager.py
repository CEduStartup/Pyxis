"""This module contains event sender and receiver.
"""

import beanstalkc
import pickle

from config import mq
from shared.events import Event
from gevent.queue import Queue
import gevent

class EventManagerError(Exception):

    """Base class for all EventManager errors.
    """


class EventSenderError(EventManagerError):

    """Base class for all EventSender errors.
    """


class EventReceiverError(EventManagerError):

    """Base class for all EventReciver errors.
    """


class UnserializableEvent(EventSenderError):

    """Sender cannot serialize event.
    """


class EventManagerBase(object):

    """Base class for event sender and event receiver.
    """

    def __init__(self, server_host=mq.queue_host, server_port=mq.queue_port):
        """Initialize event manager.

        :Parameters:
            - `server_host`: string which contains hostname where the
              beanstalkd server located.
            - `server_port`: integer value of the port to connect to.
            - `tube`: string which contains a name of the tube.
        """
        self._client = beanstalkc.Connection(host=server_host, port=server_port)
        self._client.connect()

    def __del__(self):
        """Destructor is responsible for safety connection closing.
        """
        self._client.close()


class EventSender(EventManagerBase):
    queue = None

    def __init__(self, *args, **kwargs):
        EventManagerBase.__init__(self, *args, **kwargs)
        self.queue = Queue()
        gevent.spawn(self.process_queue)
        
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
        event_cls = Event.get_event(eid)
        return event_cls(**kwargs)

    def _serialize_event(self, event):
        """Serialize an event to string using pickle module.

        :Exception:
            - `UnserializableEvent`: in case when the given event cannot be
              serialized.
        """
        try:
            return event.serialize()
        except Event.EventSerializationError, err:
            raise UnserializableEvent(str(err))

    def _get_destination(self, eid, dest=None):
        """Return a tuple with tubes suitable from event with the given `eid`.

        :Parameters:
            - `eid`: string with EID.
            - `dest`: string (or list of strings) which contains tubes for
              ivent. In case when it's None, default destinations for event
              whith such `eid` will be returned.

        :Exception:
            - `NoSuchEventError`: in case when there is not event with such
              `eid`.
        """
        res_dest = []
        if dest is not None:
            if isinstance(dest, str):
                res_dest.append(dest)
            elif isinstance(dest, (list, tuple)):
                res_dest.extend(dest)
        else:
            res_dest.extend(Event.get_tubes(eid))

        return res_dest

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
        dest = self._get_destination(event.eid, tubes)
        self.queue.put((serialized_event, dest))

    def process_queue(self):
        while True:
            (serialized_event, dest) = self.queue.get()
            for tube in dest:
                try:
                    self._client.use(tube)
                    self._client.put(serialized_event)
                except (beanstalkc.UnexpectedResponse,
                    beanstalkc.CommandFailed), err:
                    raise EventSenderError(str(err))


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
        self._client.ignore('default')
        for tube in self._tubes:
            self._client.watch(tube)

    def dispatch(self):
        """ Method that receive from message queue, restore and throw events to
        subscribed callback.
        """
        self._subscribe()

        while True:
            job = self._client.reserve()
            try:
                event = pickle.loads(job.body)
                self._callback(event)
            finally:
                job.delete()

