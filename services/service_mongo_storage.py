# Service working with trackers.
# All services are launched automatically by services/services_launcher.py.

from pymongo.connection import Connection

from config import storage
from services.service_base import SharedService
from services.service_trackers import django_orm_adapter
from shared.db.mongo_storage import TimeBasedData


from pprint import pprint as pp

aggregation_methods_map = {
    'min': 'Minimal',
    'max': 'Maximal',
    'avg': 'Average',
    'sum': 'Summed up',
    'count': 'Summed up',
}

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
        db_adapter = django_orm_adapter()
        db_adapter.connect()

        tracker_configs = db_adapter.get_trackers(tracker_id=tracker_id)
        values = {}
        for tracker in tracker_configs:
            values.update(tracker.get_values())
        pp(values)

        #res = self.query(1, 'minute', date_from='2011-10-16', date_to='2011-10-19', periods_in_group=15,
        #                 src_parms=(('1_2', 'min'), ('1_2', 'max'), ('1_2', 'avg'), ('1_1', 'min'), ('1_1', 'max'), ('1_1', 'avg')))
        if not src_parms:
            src_parms=(('2', 'min'), ('2', 'max'), ('2', 'avg'), ('3', 'min'), ('3', 'max'), ('3', 'avg'))
        res = self.query(tracker_id, period, src_parms=src_parms,
                         date_from=date_from, date_to=date_to,
                         periods_in_group=periods_in_group)
        for row in res:
            value_id, aggr = row['name']
            value_name = values[value_id]['name']
            aggr_method = aggregation_methods_map.get(aggr, '')
            row['name'] = '%s Value for %s' % (aggr_method, value_name)
        return res

if __name__ == '__main__':
    from config.services import mongo_storage
    from gevent import monkey
    monkey.patch_all()
    MongoStorage.set_config(mongo_storage)
    s = MongoStorage.start()
    s.join()

