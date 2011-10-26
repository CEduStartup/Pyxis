# This file provides API for shared services.
# Each service defined in $ROOT_DIR/services/ should have API class derived from
# service_api_base

# Usage: from services.aervices_api import trackers_api
# trackers_api.method(<params>)

from config.services import trackers as trackers_config
from config.services import launcher as launcher_config
from shared.trackers.Tracker import Tracker
import bjsonrpc
import zlib
import cPickle
import base64
import time

class method_wrapper:
    """This class acts as a proxy which bypasses request to bjsonrpc server."""
    def __call__(self, *args, **kargs):
        return self.deserialize(self.proxy_method(*args, **kargs))

    def deserialize(self, data):
        """Decompresses and de-serialises data received from bjsonrpc server."""
        return cPickle.loads(zlib.decompress(base64.decodestring(data)))

    def proxy_method(self, *args, **kargs):
        return getattr(self.connection.call, self.method_name)(*args, **kargs)


class service_api_base:
    """Base class for shared services API.

    All API classes for all shared services must be derived from it.
    """
    def __init__(self):
        self.connection = bjsonrpc.connect(self.config.bind_host,
                                           self.config.bind_port)

    def __getattr__(self, x):
        if x == 'notify':
            return self.connection.notify
        obj = method_wrapper()
        obj.method_name = x
        obj.connection = self.connection
        return obj


class trackers_api(service_api_base):
    """API for trackers stuff."""
    config = trackers_config


class launcher_api(service_api_base):
    """API for launcher."""
    config = launcher_config



if __name__ == '__main__':
    def get_trackers_test():
        N = 100
        start_time = time.time()
        for i in range(N):
            data = trackers_api.get_trackers()
            print len(data)

        end_time = time.time()
        print '%s calls executed; execution time: %0.1f seconds' %(N, end_time-start_time)

    def save_trackers_test():
        N = 1500
        start_time = time.time()
        for i in range(N):
            tracker = Tracker(None, None)
            tracker.tracker_id = i+70000
            tracker.source_type = 1
            tracker.data_type = 1
            tracker.name = 'tracker %s' %tracker.tracker_id
            tracker.description = 'tracker %s' %tracker.tracker_id
            tracker.interval = 300
            trackers_api.save_tracker(pickle.dumps(tracker))

        end_time = time.time()
        print '%s calls executed; execution time: %0.1f seconds' %(N, end_time-start_time)

    trackers_api = trackers_api()
    get_trackers_test()
    #save_trackers_test()
