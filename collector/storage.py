##
## Data storage module.
##
import gevent
from pymongo import Connection
from gevent.queue import PriorityQueue, Queue


class Storage:
    """Base class for storages."""
    dbname = None
    connection = None
    # Data first are being put into the queue, which is processed asyncronously.
    to_store_queue = None

    def __init__(self, host, port, dbname):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.to_store_queue = PriorityQueue()

    def _connect(self):
        raise RuntimeError('Abstract method')

    def put(tracker, data):
        raise RuntimeError('Abstract method')

    def start(self):
        self._connect()
        gevent.spawn(self._process_queue)

    def _process_queue(self):
        while(True):
            (tracker, data) = self.to_store_queue.get()
            self._write_to_db(data)


class MongoDBStorage(Storage):
    def _connect(self):
        self.connection = Connection(self.host, self.port)
        self.db = self.connection[self.dbname]

    def put(tracker, data):
        self.to_store_queue.put((tracker, data))

    def _write_to_db(self, tracker, data):
        data['tracker_id'] = tracker.tracker_id
        self.db['data'].insert(data)


storage_types = {'mongodb': MongoDBStorage}
