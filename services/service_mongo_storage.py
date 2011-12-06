# Service working with trackers.
# All services are launched automatically by services/services_launcher.py.

from pymongo.connection import Connection

from config import storage
from services.service_base import SharedService
from services.service_trackers import django_orm_adapter
from shared.db.mongo_storage import TimeBasedData


from pprint import pprint as pp


class MongoStorage(SharedService, TimeBasedData):
    """Trackers shared service.

    This shared service exports operations on trackers.
    """
    def _setup(self):
        self.conn = Connection('%s:%s' % (storage.host, storage.port))
        self.db = self.conn[storage.db_name]

    def _shutdown(self):
        self.conn.disconnect()

    def get_tracker_data(self, tracker_id, period, src_parms=None,
                         date_from=None, date_to=None,
                         periods_in_group=1):

        if not src_parms:
            src_parms=(('2', 'min'), ('2', 'max'), ('2', 'avg'), ('3', 'min'), ('3', 'max'), ('3', 'avg'))
        data = self.query(tracker_id, period, src_parms=src_parms,
                          date_from=date_from, date_to=date_to,
                          periods_in_group=periods_in_group)
        return self.serialize(data)


if __name__ == '__main__':
    from config.services import mongo_storage
    from gevent import monkey
    monkey.patch_all()
    MongoStorage.set_config(mongo_storage)
    s = MongoStorage.start()
    s.join()

