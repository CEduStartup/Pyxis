import pickle


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

