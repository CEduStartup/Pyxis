##
## Data storage module.
##
import gevent
from pymongo import Connection
from gevent.queue import Queue
from shared.Utils import get_date_str, rollup_periods

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


class MongoDBStorage(Storage):
    def _connect(self):
        self.connection = Connection(self.host, self.port)
        self.db = self.connection[self.dbname]

    def put(self, tracker, data):
        self.to_store_queue.put((tracker, data))

    def _write_to_db(self, tracker, data):
        ts = data['timestamp']
        tracker_id = data['tracker_id']
        values = data['values']
        for rollup_period in rollup_periods:
            collection = self.db[rollup_period]
            date = get_date_str(rollup_period, ts)
            res = collection.find_one({'tracker_id': tracker_id,
                                       'date': date})
            if res is None:
                res = {'tracker_id': tracker_id, 'date': date,
                       'values': {}}
                for xpath_id, value in values.iteritems():
                    res['values'][xpath_id] = {'min': value, 'max': value,
                                               'sum': value, 'count': 1}
                collection.save(res)
            else:
                for xpath_id, value in values.iteritems():
                    tracker_values = res['values'][xpath_id]
                    tracker_values['sum'] += value
                    tracker_values['count'] += 1
                    if tracker_values['min'] > value:
                        tracker_values['min'] = value
                    if tracker_values['max'] < value:
                        tracker_values['max'] = value
                collection.update({'_id': res['_id']}, res, True)


storage_types = {'mongodb': MongoDBStorage}
