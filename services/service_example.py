# This is an example of shared service creation.

# Import SharedService - base class for all services.
from services.service_base import SharedService

# Define your own service class.
class ExampleService(SharedService):
    # Methods your service export.
    def test(self):
        return 'Hello World'


# After this is done, add entry for your service to config/services.py and
# re-run services/services_launcher.py which will autiomatically run your service.
