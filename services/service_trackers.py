# Service working with trackers.
# All services are launched automatically by services/services_launcher.py.

from services.service_base import SharedService
from shared.trackers.Tracker import Tracker
from webui.frontend.models import *
import pickle


class db_adapter:
    """Base class for database adapters for tracking database."""
    def connect(self):
        raise RuntimeError('Abstract Method !')

    def save_tracker(self, tracker):
        """Save tracker into database.

        :Parameters:
            `tracker`: instance of shared/trackers.
        """
        raise RuntimeError('Abstract Method !')

    def get_tracker(seld, tracker_id):
        raise RuntimeError('Abstract Method !')

    def get_trackers(self, modified_since=None):
        raise RuntimeError('Abstract Method !')


class pgsql_adapter(db_adapter):
    """Database adapter which gets data from PostgreSQL database."""
    def connect(self):
        self.connection = pgdb.connect(db.db_name, host=db.db_host,
            user=db.db_user, password=db.db_password)

    def save_tracker(self, tracker):
        cursor = self.connection.cursor()
        sql = """\
insert into trackers (tracker_id, name, description, source_type, data_type,
interval) values(%s, '%s', '%s', %s, %s, %s)""" %(tracker.get_id(), tracker.name,
tracker.description, tracker.source_type, tracker.data_type, tracker.interval)
        cursor.execute(sql)
        self.connection.commit()
        cursor.close()

    def get_tracker(seld, tracker_id):
        pass

    def get_trackers(self, modified_since=None):
        cursor = self.connection.cursor()
        cursor.execute('select * from trackers')
        trackers_raw = cursor.fetchall()
        tracker_objects = []
        for (tracker_id, name, description, created, last_modified, status,
             source_type, data_type, source, interval) in trackers_raw:
            tracker = Tracker(tracker_id, source, source_type, '', interval,
                              None)
            tracker_objects.append(tracker)

        cursor.close()
        return tracker_objects


class django_orm_adapter(db_adapter):
    """Database adapter which gets data from DJango ORM."""
    def connect(self):
        pass

    def get_tracker(seld, tracker_id):
        pass

    def get_trackers(self, modified_since=None):
        """Return trackers modified since given time."""
        trackers = []
        model_objects = TrackerModel.objects.all()
        for model_object in model_objects:
            trackers.append(self._tracker_from_model(model_object))

        return trackers

    def _tracker_from_model(self, model_object):
        """Method constructs shared.trackers.Tracker object from TrackerModel
        DJango representation."""
        datasources = []
        for ds in model_object.datasourcemodel_set.all():
            access_method = ds.access_method.name
            data_type = ds.data_type.name
            query = ds.query
            values = []
            for value in ds.valuemodel_set.all():
                value_dict = {'value_id': value.id,
                              'name': value.extraction_rule,
                              'type': value.type}
                values.append(value_dict)
            datasource = {'access_method': access_method,
                          'query': query,
                          'data_type': data_type,
                          'values': values}

        return Tracker(model_object.id, model_object.refresh_interval, datasources)


class TrackersService(SharedService):
    """Trackers shared service.

    This shared service exports operations on trackers.
    """
    def _setup(self):
        self.db_adapter = django_orm_adapter()
        self.db_adapter.connect()

    def get_trackers(self, modified_since=None):
        """Get list of trackers.

        :Parameters:
            - `modified_since`: retrieve only trackers modified since given time.

        :Return:
            - list of trackers objects (shared.trackers.Tracker) pickled by
              pickle module (use import pickle; pickle.loads(result) to unpickle)
        """
        # Stub for now.
        data = self.db_adapter.get_trackers(modified_since=modified_since)
        return self.serialize(data)

    def save_tracker(self, tracker):
        self.db_adapter.save_tracker(pickle.loads(tracker))


if __name__ == '__main__':
    db_adapter = django_orm_adapter()
    db_adapter.connect()
    import time

    start_time = time.time()
    data = db_adapter.get_trackers()
    pickled = pickle.dumps(data)
    compressed = zlib.compress(pickled, 9)
    b64 = base64.encodestring(pickled)
    print time.time() - start_time

