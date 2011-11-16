##
## Data storage module.
##
import gevent
from config import storage
from pymongo import Connection
from gevent.queue import Queue
from shared.db.mongo_storage import TimeBasedData


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
            self._write_to_db(tracker, data)

    def get_store_queue_size(self):
        return self.to_store_queue.qsize()

    def put(self, tracker, data):
        raise RuntimeError('Abstract method')

    def start(self):
        self._connect()
        gevent.spawn(self._process_queue)


class MongoDBStorage(Storage, TimeBasedData):
    def _connect(self):
        self.conn = Connection('%s:%s' % (storage.host, storage.port))
        self.db = self.conn[storage.db_name]

    def put(self, tracker, data):
        self.to_store_queue.put((tracker, data))

    def _write_to_db(self, tracker_id, timestamp, data):
        """Inserts `data` to the MongoDB and aggregates data in `hour` and
        `day` periods.

        :Parameters:

            - `tracker_id`: id of data source group;

            - `timestamp`: date of data retrieval;

            - `data`: dictionary with values to insert in format
              { <value_id>: <value>, }
        """
        self.insert_raw_data(self, tracker_id, timestamp, data)

storage_types = {'mongodb': MongoDBStorage}
