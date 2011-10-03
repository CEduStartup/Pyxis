# Module starts all services defined in config/srv_config and services/service.py
# All services are run under gevent.
from config.srv_config import trackers as config
import bjsonrpc


class method_wrapper:
    def __call__(self, *args, **kargs):
        return self.proxy_method(*args, **kargs)

    def proxy_method(self, *args, **kargs):
        connection = bjsonrpc.connect(self.config.bind_host, self.config.bind_port)
        return getattr(connection.call, self.method_name)(*args, **kargs)


class service_base:
    def __getattr__(self, x):
        obj = method_wrapper()
        obj.method_name = x
        return obj


class trackers(service_base):
    self.config = config


