# Service working with trackers.
# All services are launched automatically by services/services_launcher.py.

import base64
import pickle
import zlib

from frontend.models import TrackerModel
from services.service_base import SharedService
from shared.trackers.Tracker import Tracker
from shared import Utils


class db_adapter:
    """Base class for database adapters for tracking database."""
    def connect(self):
        raise RuntimeError('Abstract Method !')

    def get_trackers(self, modified_since=None):
        raise RuntimeError('Abstract Method !')


class django_orm_adapter(db_adapter):
    """Database adapter which gets data from DJango ORM."""
    def connect(self):
        pass

    def get_trackers(self, modified_since=None, tracker_id=None):
        """Return trackers modified since given time."""
        trackers = []
        search_parms = {}
        if modified_since is not None:
            search_parms['last_modified__gte'] = Utils.time2str(modified_since)
        if tracker_id is not None:
            search_parms['id'] = tracker_id
        if not search_parms:
            model_objects = TrackerModel.objects.all()
        else:
            model_objects = TrackerModel.objects.filter(**search_parms)
        for model_object in model_objects:
            trackers.append(self._tracker_from_model(model_object))

        return trackers

    def _tracker_from_model(self, model_object):
        """Method constructs shared.trackers.Tracker object from TrackerModel
        DJango representation."""
        datasources = []
        for ds in model_object.datasourcemodel_set.all():
            access_method = ds.access_method
            data_type = ds.data_type
            query = ds.query
            values = []
            for value in ds.valuemodel_set.all():
                value_dict = {'value_id': value.id,
                              'extraction_rule': value.extraction_rule,
                              'name': value.name,
                              'type': value.value_type}
                values.append(value_dict)
            datasource = {'access_method': access_method,
                          'query': query,
                          'data_type': data_type,
                          'values': values}
            datasources.append(datasource)

        return Tracker(model_object.id, model_object.refresh_interval,
                       datasources, tracker_name=model_object.name)


class TrackersService(SharedService):
    """Trackers shared service.

    This shared service exports operations on trackers.
    """
    def _setup(self):
        self.db_adapter = django_orm_adapter()
        self.db_adapter.connect()

    def get_trackers(self, modified_since=None,
                           tracker_id=None):
        """Get list of trackers.

        :Parameters:
            - `modified_since`: retrieve only trackers modified since given time.

        :Return:
            - list of trackers objects (shared.trackers.Tracker) pickled by
              pickle module (use import pickle; pickle.loads(result) to unpickle)
        """
        # Stub for now.
        data = self.db_adapter.get_trackers(modified_since=modified_since,
                                            tracker_id=tracker_id)
        return self.serialize(data)


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

