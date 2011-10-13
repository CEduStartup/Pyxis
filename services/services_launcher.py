# Module starts all services defined in config/services.py.
# All services are run under gevent.
import config.services as config
from services.service_base import SharedService
import types
import gevent
from gevent import monkey


def start_service(service_config):
    """Start one service.

    :Parameters:
        - `service_config`: class defining a service. See config/services.py
    """
    module = __import__('services.%s' %service_config.module,
                        fromlist=(service_config.module))
    service_class = getattr(module, service_config.handler)
    service_class.set_config(service_config)
    print 'Started %s' %service_config.description
    return service_class.start()


def _is_service_config_class(attribute):
    """Determine if given module attribute is a shared service configuration
    class."""
    return (isinstance(attribute, types.ClassType) and
            issubclass(attribute, config.SharedServiceConfig) and
            attribute.description)


def launch_services():
    """Launch all services defined in config/services.py."""
    print 'Starting services...'
    threads = []
    for attribute in dir(config):
        attribute = getattr(config, attribute)
        if _is_service_config_class(attribute):
            service_config = attribute
            if service_config.active:
                threads.append(start_service(service_config))
            else:
                print 'Service disabled by administrator: %s' %service_config.description

    gevent.joinall(threads)


if __name__ == '__main__':
    monkey.patch_all()
    launch_services()
