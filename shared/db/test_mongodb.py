from pymongo.connection import Connection
from shared.db.mongo_storage import TimeBasedData
from config import storage


if __name__ == '__main__':
    conn = Connection('%s:%s' % (storage.host, storage.port))

    data_storage = TimeBasedData()
    data_storage.conn = conn
    data_storage.db = conn[storage.db_name]

    data_storage.clear_db()
    data_storage.fill_test_data(tracker_id=1, value_ids=(2,3,4), date_from='2011-01-01')
    #print data_storage.query(1, 'minute', date_from='2011-10-15', date_to='2011-10-19', periods_in_group=15,
    #                   src_parms=(('1_1', 'sum'), ('1_1', 'min'), ('1_1', 'max'), ('1_1', 'avg')))
