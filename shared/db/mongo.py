from shared.Utils import rollup_periods, get_date_str, value_generator, \
                         get_from_to_range, FIVE_MIN
import time




from pprint import pprint as pp


class TimeBasedData(object):
    connection = None
    db = None

    def clear_db(self, collection=None):
        """Remove all items from collection `collection`.

        :Parameters:

            - `collection`: collection name which should be cleaned.
              If not specified, all collectionns will be cleared.
        """
        if collection:
            collection = [collection,]
        else:
            collection = self.db.collection_names()
        for i in collection:
            self.db[i].remove({})

    def fill_test_data(self, trackers_count=5, xpaths_per_tracker=3,
                       date_from=None, date_to=None, duration_in_days=365):
        """Fill in the MongoDb with the test data.

        :Parameters:

            - `trackers_count`: number of trackers to fill data;

            - `xpaths_per_tracker`: number of xpath for one tracker;

            - `date_from`: date in format *%Y-%m-%d*;

            - `date_to`: date in format *%Y-%m-%d*;

            - `duration_in_days`: period for which fill in test data. Can be
               used with either `date_from` or `date_to`. If both `date_from`
               and `date_to` are specified `duration_in_days` will be omitted.
        """
        vg = value_generator(5)
        ts_from, ts_to = get_from_to_range(date_from, date_to, duration_in_days)

        for ts in range(ts_from, ts_to, FIVE_MIN):
            for tracker_id in range(1, trackers_count+1):
                values = {}
                for i in range(1, xpaths_per_tracker+1):
                    xpath_id = '%s_%s' % (tracker_id, i)
                    values[xpath_id] = vg.next()
                self.insert_raw_data(tracker_id, ts, values)

    def insert_raw_data(self, tracker_id, timestamp, data):
        """Inserts `data` to the MongoDB and aggregates data in `1hour` and
        `1day` periods.

        :Parameters:

            - `tracker_id`: trackers id to insert data;

            - `timestamp`: date of data retrieval;

            - `data`: dictionary with values to insert in format
              { <xpath_id>: <value>, }
        """
        for period_name in rollup_periods:
            collection = self.db[period_name]
            date = get_date_str(timestamp, period_name)
            res = collection.find_one({'date': date, 'tracker_id': tracker_id})
            if res is None:
                values = {}
                res = {'tracker_id': tracker_id, 'date': date, 'values': values}
                for xpath_id, value in data.iteritems():
                    values[xpath_id] = {'min': value, 'max': value,
                                        'sum': value, 'count': 1}
                collection.save(res)
            else:
                values = res['values']
                for xpath_id, value in data.iteritems():
                    if not xpath_id in values:
                        values[xpath_id] = {'min': value, 'max': value,
                                            'sum': value, 'count': 1}
                    else:
                        values[xpath_id]['sum'] += value
                        values[xpath_id]['count'] += 1
                        if values[xpath_id]['min'] > value:
                            values[xpath_id]['min'] = value
                        if values[xpath_id]['max'] < value:
                            values[xpath_id]['max'] = value
                collection.update({'_id': res['_id']}, res, True)
    def query(self, tracker_id, source_id, rollup_period, date_from=None,
              date_to=None, aggregation_function='avg', periods_in_group=1):
        date_from, date_to = map(get_date_str,
                                 get_from_to_range(date_from, date_to))
        collection = self.db[rollup_period]
        res = collection.find({'tracker_id': tracker_id,
                               'date': {'$gte': date_from, '$lt': date_to}})
        for r in res:
            pp(r)



ts_from, ts_to = get_from_to_range()
print get_date_str(ts_to)
print time.localtime(ts_to)

