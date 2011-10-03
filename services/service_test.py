import bjsonrpc
#import pgdb
#import config.db as db_config, config.srv as srv_config
from services.service_base import SharedService


class TestService(SharedService):
    def test(modified_since=None):
        return 'Hello World'

