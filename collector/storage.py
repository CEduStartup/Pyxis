##
## Data storage module.
##
import gevent
from pymongo import Connection
from gevent.queue import Queue


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
        self.to_store_queue = Queue()

    def _connect(self):
        raise RuntimeError('Abstract method')

    def _process_queue(self):
        while(True):
            (tracker, data) = self.to_store_queue.get()
            self._write_to_db(data)
    
    def get_store_queue_size(self):
        return self.to_store_queue.qsize()

    def put(tracker, data):
        raise RuntimeError('Abstract method')

    def start(self):
        self._connect()
        gevent.spawn(self._process_queue)


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
