# This file provides API for shared services.
# Each service defined in $ROOT_DIR/services/ should have API class derived from
# service_api_base

# Usage: from services.aervices_api import trackers_api
# trackers_api.method(<params>)
from config.srv_config import trackers as trackers_config
import bjsonrpc


class method_wrapper:
    """This class acts as a proxy which bypasses request to bjsonrpc server."""
    def __call__(self, *args, **kargs):
        return self.proxy_method(*args, **kargs)

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
        obj = method_wrapper()
        obj.method_name = x
        obj.connection = self.connection
        return obj


class trackers_api(service_api_base):
    """API for trackers stuff. """
    config = trackers_config


if __name__ == '__main__':
    o = trackers_api()
    import time

    N = 1000
    start_time = time.time()
    for i in range(N):
        print o.get_trackers()

    end_time = time.time()

    print '%s calls executed; execution time: %0.1f seconds' %(N, end_time-start_time)
