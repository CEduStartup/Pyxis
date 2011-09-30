# Base class for all shared services.
# All shared services must be derived from given class.
# Services are run automatically by services/services_launcer.py
import bjsonrpc
import gevent


class SharedService(bjsonrpc.handlers.BaseHandler):
    @classmethod
    def set_config(self, config):
        self.config = config

    @classmethod
    def start(self):
        server = bjsonrpc.createserver(host=self.config.bind_host,
                                       port=self.config.bind_port,
                                       handler_factory=self)
        gevent.spawn(server.serve)

