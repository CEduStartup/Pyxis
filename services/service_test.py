import bjsonrpc
import pgdb
from config import db_config
from config import srv_config
from services.service_base import SharedService


class TestService(SharedService):
    def test(modified_since=None):
        return 'Hello World'

