import pymongo
import time

from shared.Utils import rollup_periods, get_date_str, value_generator, \
                         get_from_to_range, duration_in_seconds, time_round, \
                         ONE_MINUTE, ONE_HOUR, ONE_DAY
from random import randint

from pprint import pprint as pp


def x_keys_time_based(ts_from, ts_to, period, periods_in_group=1):
    keys = []
    d = duration_in_seconds[period]
    ts = ts_from
    while ts < ts_to:
        ts = time_round(ts, period)
        if not ts in keys:
            keys.append(ts)
        ts += d * periods_in_group
    return keys


class TimeBasedData(object):
    connection = None
    db = None

    def clear_db(self):
        """Remove all items from mongodb."""
        self.db['data'].remove({})
        self.db['data'].create_index([('tracker_id', pymongo.ASCENDING),
                                      ('timestamp', pymongo.ASCENDING)])

    def fill_test_data(self, tracker_id=1, value_ids=[],
                       date_from=None, date_to=None, duration_in_days=365):
        """Fill in the MongoDb with the test data.

        :Parameters:

            - `tracker_id`: id of datasource group;

            - `value_ids`: list of `value_id` related to this tracker;

            - `date_from`: date in format *%Y-%m-%d*;

            - `date_to`: date in format *%Y-%m-%d*;

            - `duration_in_days`: period for which fill in test data. Can be
               used with either `date_from` or `date_to`. If both `date_from`
               and `date_to` are specified `duration_in_days` will be omitted.
        """
        vg = value_generator(5)
        ts_from, ts_to = get_from_to_range(date_from, date_to, period='day',
                                           periods_count=duration_in_days)
        for value_id in value_ids:
            value_id = str(value_id)
            print '\n\nFilling db for %s' % value_id
            ts = ts_from
            while ts < ts_to:
                insertions = 0
                for i in range(24):
                    has_data_in_hour = randint(0, 1)
                    if not has_data_in_hour:
                        continue
                    j = 0
                    while j < 60:
                        values = {value_id: vg.next()}
                        d = ts + i*ONE_HOUR + j*ONE_MINUTE
                        self.insert_raw_data(tracker_id, d, values)
                        j += randint(1, 20)
                        insertions += 1
                if insertions:
                    print '\t%s < %s items' % (get_date_str(ts, 'day'), insertions)
                ts += ONE_DAY
                
    def ensure_string_keys(self, data):
        """ Returns data with keys, which are string types. """
        result = {}
        for value_id in data:
            result[str(value_id)] = data[value_id]
        return result


    def insert_raw_data(self, tracker_id, timestamp, data):
        """Inserts `data` to the MongoDB and aggregates data in `1hour` and
        `day` periods.

        :Parameters:

            - `tracker_id`: id of data source group;

            - `timestamp`: date of data retrieval;

            - `data`: dictionary with values to insert in format
              { <value_id>: <value>, }
        """
        if not 'data' in self.db.collection_names():
            self.db['data'].create_index([('tracker_id', pymongo.ASCENDING),
                                          ('timestamp', pymongo.ASCENDING)])
        collection = self.db['data']
        day_ts = time_round(timestamp, 'day')
        res = collection.find_one({'tracker_id': tracker_id,
                                   'timestamp': day_ts})
        if res is None:
            doc = {
                'tracker_id': tracker_id,
                'timestamp': day_ts,
                'raw': {},
                'hour': {},
                'day': {},
            }
        else:
            doc = res
        data = self.ensure_string_keys(data)
        doc['raw'][str(int(timestamp))] = data # we should use 'validators' conception in this
        for period in ('hour', 'day'):
            ts = str(time_round(timestamp, period))
            if not ts in doc[period]:
                doc[period][ts] = {}
            values = doc[period][ts]
            for value_id, value in data.iteritems():
                if not value_id in values:
                    values[value_id] = {'value': value, 'min': value,
                                        'max': value, 'sum': value,
                                        'count': 1}
                else:
                    values[value_id]['value'] = value
                    values[value_id]['sum'] += value
                    values[value_id]['count'] += 1
                    if values[value_id]['min'] > value:
                        values[value_id]['min'] = value
                    if values[value_id]['max'] < value:
                        values[value_id]['max'] = value
        if res is None:
            print doc
            collection.save(doc)
        else:
            collection.update({'_id': doc['_id']}, doc, True)

    def query(self, tracker_id, period, src_parms=None, date_from=None,
              date_to=None, periods_in_group=1):
        """Query MongoDB and aggregate data by the rollup period and source.

        :Parameters:

            - `tracker_id`: id of data source group;

            - `period`: minimal interval which will be displayed on graph;

            - `src_parms`: list of pairs: (<source-id>, <aggregation-method>);

            - `date_from`: date from string in format `%Y-%m-%d %H:%M`;

            - `date_to`: date to string in format `%Y-%m-%d %H:%M`;
        """
        print '='*50
        print tracker_id, period, src_parms, date_from, date_to, periods_in_group
        print '='*50
        collection = self.db['data']
        selection_key = period
        if selection_key == 'minute':
            selection_key = 'raw'
        elif selection_key == 'week':
            selection_key = 'day'
        elif selection_key == 'month':
            selection_key = 'day'
        if period in ('minute', 'hour'):
            ts_from, ts_to = get_from_to_range(date_from, date_to, period='day')
        else:
            ts_from, ts_to = get_from_to_range(date_from, date_to, period=period)
        print 'for `day`:', get_date_str(ts_from, 'day'), get_date_str(ts_to, 'day')
        print 'for `%s`:' % period, get_date_str(ts_from, period), get_date_str(ts_to, period)
        print 'for `minute`:', get_date_str(ts_from, 'minute'), get_date_str(ts_to, 'minute')
        res = collection.find({'tracker_id': tracker_id,
                               'timestamp': {'$gte': ts_from, '$lt': ts_to}},
                              [selection_key])
        ts_keys = x_keys_time_based(ts_from, ts_to, period, periods_in_group)
        ts_keys.append(ts_to)
        db_data = {}
        for item in res:
            for timestamp, values in item[selection_key].iteritems():
                if int(timestamp) < ts_from or int(timestamp) >= ts_to:
                    continue
                db_data[int(timestamp)] = values
        if db_data:
            min_ts = min(db_data.keys())
            max_ts = max(db_data.keys())
            print 'Data in DB:', get_date_str(min_ts, period), get_date_str(max_ts, period), len(db_data.keys())
        groups = {}
        i = 0
        f, t = ts_keys[i], ts_keys[i+1]
        for ts in sorted(db_data.keys()):
            while not (f <= ts < t):
                i += 1
                f, t = ts_keys[i], ts_keys[i+1]
            if not i in groups:
                groups[i] = []
            groups[i].append(ts)
        ts_keys.pop()
        data_map = {}
        for value_id, aggr in src_parms:
            data_map[(value_id, aggr)] = [0] * len(ts_keys)
        last_key = None
        tmp_vals = None
        for idx in sorted(groups):
            grouped_values = {}
            for value_id, aggr in src_parms:
                grouped_values[value_id] = {
                    'min': None, 'max': None,
                    'sum': 0, 'count': 0,
                }
            for ts in groups[idx]:
                item = db_data[ts]
                for value_id, aggr in src_parms:
                    if not value_id in item:
                        continue
                    values = item[value_id]
                    if selection_key == 'raw':
                        values = {
                            'min': values, 'max': values,
                            'sum': values, 'count': 1,
                        }
                    if grouped_values[value_id]['min'] is None or \
                       grouped_values[value_id]['min'] > values['min']:
                        grouped_values[value_id]['min'] = values['min']
                    if grouped_values[value_id]['max'] is None or \
                       grouped_values[value_id]['max'] < values['max']:
                        grouped_values[value_id]['max'] = values['max']
                    grouped_values[value_id]['sum'] += values['sum']
                    grouped_values[value_id]['count'] += values['count']
            for (value_id, aggr), data in data_map.iteritems():
                if aggr == 'avg':
                    if grouped_values[value_id]['count']:
                        data[idx] = round(1.0 * grouped_values[value_id]['sum'] /
                                          grouped_values[value_id]['count'], 2)
                    else:
                        data[idx] = 0
                else:
                    if aggr == 'raw':
                        aggr = 'sum'
                    data[idx] = grouped_values[value_id][aggr] or 0

        tracker_data = []
        for (value_id, aggr), data in data_map.iteritems():
            tracker_data.append({
                'name': (int(value_id), aggr),
                'data': data,
                'pointInterval': duration_in_seconds[period]*periods_in_group * 1000,
                'pointStart': (ts_from - time.timezone) * 1000,
            })

        return tracker_data

