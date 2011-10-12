from shared.Utils import rollup_periods, get_date_str, value_generator, \
                         get_from_to_range, periods_mapping, ONE_MIN
from random import randint

from pprint import pprint as pp


def x_keys_time_based(rollup_period, ts_from, ts_to,
                      periods_in_group=1):
    keys = []
    d = periods_mapping[rollup_period]
    for ts in range(ts_from, ts_to, d*periods_in_group):
        key =  et_date_str(ts, rollup_period)
        if not key in keys:
            keys.append(key)
    return keys


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

    def fill_test_data(self, trackers_count=1, xpaths_per_tracker=2,
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
        ts_from, ts_to = get_from_to_range(date_from, date_to, rollup_period='1day',
                                           periods_count=duration_in_days)

        ts = ts_from
        while ts < ts_to:
            for tracker_id in range(1, trackers_count+1):
                values = {}
                for i in range(1, xpaths_per_tracker+1):
                    src_id = '%s_%s' % (tracker_id, i)
                    values[src_id] = vg.next()
                self.insert_raw_data(tracker_id, ts, values)
            ts += ONE_MIN * randint(1, 15)

    def insert_raw_data(self, tracker_id, timestamp, data):
        """Inserts `data` to the MongoDB and aggregates data in `1hour` and
        `1day` periods.

        :Parameters:

            - `tracker_id`: id of data source group;

            - `timestamp`: date of data retrieval;

            - `data`: dictionary with values to insert in format
              { <src_id>: <value>, }
        """
        for period_name in rollup_periods:
            collection = self.db[period_name]
            date = get_date_str(timestamp, period_name)
            res = collection.find_one({'date': date, 'tracker_id': tracker_id})
            if res is None:
                values = {}
                res = {'tracker_id': tracker_id, 'date': date, 'values': values}
                for src_id, value in data.iteritems():
                    values[src_id] = {'min': value, 'max': value,
                                        'sum': value, 'count': 1}
                collection.save(res)
            else:
                values = res['values']
                for src_id, value in data.iteritems():
                    if not src_id in values:
                        values[src_id] = {'value': value, 'min': value,
                                          'max': value, 'sum': value,
                                          'count': 1}
                    else:
                        values[src_id]['value'] = value
                        values[src_id]['sum'] += value
                        values[src_id]['count'] += 1
                        if values[src_id]['min'] > value:
                            values[src_id]['min'] = value
                        if values[src_id]['max'] < value:
                            values[src_id]['max'] = value
                collection.update({'_id': res['_id']}, res, True)
    def query(self, tracker_id, rollup_period, src_parms=None, date_from=None,
              date_to=None, periods_in_group=1):
        """Query MongoDB and aggregate data by the rollup period and source.

        :Parameters:

            - `tracker_id`: id of data source group;

            - `rollup_period`: minimal interval which will be displayed on graph;

            - `src_parms`: list of pairs: (<source-id>, <aggregation-method>);

            - `date_from`: date from string in format `%Y-%m-%d %H:%M`;

            - `date_to`: date to string in format `%Y-%m-%d %H:%M`;
        """
        collection_name = rollup_period
        if rollup_period == '1month':
            collection_name = '1day'
        ranges = get_from_to_range(date_from, date_to, rollup_period=rollup_period)
        date_from, date_to = map(lambda x:get_date_str(x, collection_name), ranges)
        x_keys = x_keys_time_based(rollup_period, *ranges,
                                   periods_in_group=periods_in_group)
        collection = self.db[collection_name]
        res = collection.find({'tracker_id': tracker_id,
                               'date': {'$gte': date_from, '$lt': date_to}})
        data_map = {}
        for src_id, aggr in src_parms:
            d = [0] * len(x_keys)
            data_map[(src_id, aggr)] = d
        last_key = None
        tmp_vals = None
        for i in range(res.count()+1):
            try:
                item = res[i]
                key = get_date_str(item['date'], rollup_period)
            except IndexError:
                item = key = None
            if key != last_key:
                if last_key in x_keys:
                    idx = x_keys.index(last_key)
                    for (src_id, aggr) in data_map:
                        if not src_id in tmp_vals:
                            continue
                        d = data_map[(src_id, aggr)]
                        if aggr == 'avg':
                            d[idx] = 1.0 * tmp_vals[src_id]['sum'] / tmp_vals[src_id]['count']
                        else:
                            d[idx] = tmp_vals[src_id][aggr]
                tmp_vals = {}
                if item:
                    tmp_vals.update(item['values'])
                last_key = key
                continue
            for src_id, src_vals in item['values'].iteritems():
                tmp = tmp_vals.get(src_id, {})
                if 'sum' in src_vals:
                    tmp['sum'] += src_vals['sum']
                if 'count' in src_vals:
                    tmp['count'] += src_vals['count']
                if 'min' in src_vals:
                    if tmp['min'] > src_vals['min']:
                        tmp['min'] = src_vals['min']
                if 'max' in src_vals:
                    if tmp['max'] < src_vals['max']:
                        tmp['max'] = src_vals['max']
                tmp_vals[src_id] = tmp
        return {'x_keys': x_keys,
                'data': data_map}

