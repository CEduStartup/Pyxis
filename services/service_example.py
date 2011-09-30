# This is an example of shared service creation.

# Import SharedService - base class for all services.
from services.service_base import SharedService

# Define your own service class.
class TestService(SharedService):
    # This is just a description.
    description = 'test service'

    # Methods your service export.
    def test(modified_since=None):
        return 'Hello World'


# After this is done, add entry for your service to config/srv_config.py and
# re-run services/services_launcher.py which will autiomaticall run your service.

