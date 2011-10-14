import bjsonrpc
from bjsonrpc.handlers import BaseHandler
from django.conf import settings
from random import random
from pymongo.connection import Connection
from shared.db.mongo import TimeBasedData

class TrackersHandler(BaseHandler, TimeBasedData):
    def _setup(self, *args, **kwargs):
        self.conn = Connection('172.22.60.75')
        self.util_db = self.conn['util_db']

    def _shutdown(self):
        self.conn.disconnect()

    def get_tracker_data(self, id, start=0, end=0, period=False, method=False):

        res = self.query(1, '1month', date_from='2011-08-01', date_to='2011-10-13',
                       src_parms=(('1_1', 'min'), ('1_1', 'max'), ('1_1', 'avg')))
        return res


if __name__ == '__main__':
    s = bjsonrpc.createserver(host = settings.RPC_HOST,
                              port = settings.RPC_PORT,
                              handler_factory = TrackersHandler)
    s.debug_socket(True)
    s.serve()
