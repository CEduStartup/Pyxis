# This file contains shared services definition.
# Services logic are defined in services dir.

class SharedServiceConfig:
    # Service description.
    description = None
    # Should this service be run automatically ?
    active = None
    # Host to bind.
    bind_host = '127.0.0.1'
    # Port to bind.
    bind_port = None
    # Name of module under $ROOT_DIR/services.
    module = 'service_trackers'
    # Name of class inside module (described above).
    handler = 'TrackersService'


class trackers(SharedServiceConfig):
    """Service which exports methods working with Trackers."""
    description = 'trackers operations'
    active = True
    bind_host = '127.0.0.1'
    bind_port = 8000
    module = 'service_trackers'
    handler = 'TrackersService'


class test(SharedServiceConfig):
    """Test service."""
    description = 'test service'
    active = False
    bind_host = '127.0.0.1'
    bind_port = 8001
    module = 'service_test'
    handler = 'TestService'
