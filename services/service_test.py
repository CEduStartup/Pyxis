from services.service_base import SharedService


class TestService(SharedService):
    def test(modified_since=None):
        return 'Hello World'

