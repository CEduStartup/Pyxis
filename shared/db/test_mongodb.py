from pymongo.connection import Connection
from shared.db.mongo import TimeBasedData


if __name__ == '__main__':
    connection = Connection('172.22.60.75')
    #connection = Connection()
    db = connection['time-based-data']

    data_storage = TimeBasedData()
    data_storage.db = db

    #data_storage.clear_db()
    #print 'Clearing done'
    #data_storage.fill_test_data(date_from='2011-09-01')
    print data_storage.query(1, '1day', date_from='2011-08-01', date_to='2011-10-13',
                       src_parms=(('1_1', 'sum'), ('1_1', 'min'), ('1_1', 'max'), ('1_1', 'avg')))
