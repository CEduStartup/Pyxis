# This file contains shared services definition.
# Services logic are defined in services dir.

from shared.Utils import port_randomizer
from config.context import create_context


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
    bind_port = 8002 + port_randomizer()
    module = 'service_trackers'
    handler = 'TrackersService'


class launcher(SharedServiceConfig):
    """This service is used by system launcher. it is not automatically created
    by services_launcher.py."""
    description = 'System Launcher'
    active = False
    bind_host = '127.0.0.1'
    bind_port = 8999 + port_randomizer()
    module = None
    handler = None

class mongo_storage(SharedServiceConfig):
    """Service which exports methods working with MongoDB"""
    description = 'mongodb operations'
    active = True
    bind_host = '127.0.0.1'
    bind_port = 8001 + port_randomizer()
    module = 'service_mongo_storage'
    handler = 'MongoStorage'


class test(SharedServiceConfig):
    """Test service."""
    description = 'test service'
    active = False
    bind_host = '127.0.0.1'
    bind_port = 8003 + port_randomizer()
    module = 'service_test'
    handler = 'TestService'


component_name = 'shared_services'

create_context(component_name)
