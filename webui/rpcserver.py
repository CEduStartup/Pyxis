import bjsonrpc
from bjsonrpc.handlers import BaseHandler
import settings
from config import storage
from random import random
from pymongo.connection import Connection
from shared.db.mongo_storage import TimeBasedData

class TrackersHandler(BaseHandler, TimeBasedData):
    def _setup(self, *args, **kwargs):
        self.conn = Connection('%s:%s' % (storage.host, storage.port))
        self.db = self.conn[storage.db_name]

    def _shutdown(self):
        self.conn.disconnect()

    def get_tracker_data(self, tracker_id, period, src_parms=None,
                         date_from=None, date_to=None,
                         periods_in_group=1):
        #res = self.query(1, 'minute', date_from='2011-10-16', date_to='2011-10-19', periods_in_group=15,
        #                 src_parms=(('1_2', 'min'), ('1_2', 'max'), ('1_2', 'avg'), ('1_1', 'min'), ('1_1', 'max'), ('1_1', 'avg')))
        if not src_parms:
            src_parms=(('2', 'min'), ('2', 'max'), ('2', 'avg'), ('3', 'min'), ('3', 'max'), ('3', 'avg'))

        res = self.query(tracker_id, period, src_parms=src_parms,
                         date_from=date_from, date_to=date_to,
                         periods_in_group=periods_in_group)
        return res


if __name__ == '__main__':
    s = bjsonrpc.createserver(host = settings.RPC_HOST,
                              port = settings.RPC_PORT,
                              handler_factory = TrackersHandler)
    s.debug_socket(True)
    s.serve()
