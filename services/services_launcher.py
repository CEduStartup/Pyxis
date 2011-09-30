# Module starts all services defined in config/srv_config and services/service.py
# All services are run under gevent.
from config import srv_config
from services.service_base import SharedService
import types
import gevent
from gevent import monkey


def start_service(service_config):
    """Start one service.

    :Parameters:
        - `service_config`: class defining a service. See services/srv_config.py
    """
    module = __import__('services.%s' %service_config.module,
                        fromlist=(service_config.module))
    service_class = getattr(module, service_config.handler)
    service_class.set_config(service_config)
    service_class.start()
    print 'Started %s' %service_class.description


def launch_services():
    """Launch all services defined in config/srv_config.py."""
    print 'Starting services...'
    for attribute in dir(srv_config):
        attribute = getattr(srv_config, attribute)
        if 'handler' in dir(attribute):
            service_config = attribute
            start_service(service_config)

    while(True):
        gevent.sleep(0.01)


if __name__ == '__main__':
    monkey.patch_all()
    launch_services()
