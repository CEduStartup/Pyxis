import beanstalkc
import pickle


class EventReceiver(EventManagerBase):

    def __init__(self, server_host, server_port, tube, callback):
        EventReceiverBase.__init__(self, server_host, server_port, tube)
        self._callback = callback

    def dispatch(self):
        while True:
            job = self._client.reserve()
            event = pickle.loads(job.body)
            job.delete()
            self._callback(event)

