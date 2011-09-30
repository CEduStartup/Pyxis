# This file contains shared services definition.
# Services logic are defined in services dir.

class service_config(object):
    """Base class for services configuration."""

    # IP address or hostname service will be bind to. For example, 127.0.0.1 or
    # 0.0.0.0.
    bind_host = None
    # Bind port.
    bind_port = None
    # Module name under $ROOT/services.
    module = None
    # Handler class defined in given module. See services/SharedService docstring
    # for details.
    handler = None


class trackers(service_config):
    """Service which exports methods working with Trackers."""
    bind_host = '127.0.0.1'
    bind_port = 8000
    module = 'service_trackers'
    handler = 'TrackersService'


class test(service_config):
    """Test service."""
    bind_host = '127.0.0.1'
    bind_port = 8001
    module = 'service_test'
    handler = 'TestService'
