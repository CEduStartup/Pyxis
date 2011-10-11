from shared.Utils import rollup_periods, get_date_str


class TimeBasedData(Object):
    connection = None
    db = None

    def test_data(self, trackers_count=5, xpaths_per_tracker=3,
                  date_from=None, date_to=None, duration_in_days='365'):
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
            date = get_date_str(period_name, timestamp)
            res = collection.find_one({'date': date, 'tracker_id': tracker_id})
            if res is None:
                res = {'tracker_id': tracker_id, 'date': date, 'min': value,
                       'max': value, 'sum': value, 'count': 1}

