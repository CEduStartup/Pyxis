# Base class for all shared services.
# All shared services must be derived from given class.
# Services are run automatically by services/services_launcer.py
import bjsonrpc
import gevent
import zlib
import cPickle
import base64


class SharedService(bjsonrpc.handlers.BaseHandler):
    """Base class for shared services.

    Shared service are run automatically by services_starter.py, and they're
    based on bjsonrpc server under gevent.
    """
    def _setup(self):
        """This is called every time we connect to the service using
        bjsonrpc.connect()."""
        raise RuntimeError('Abstract Method !')

    @classmethod
    def set_config(self, config):
        """This is used by services launcher only."""
        self.config = config

    @classmethod
    def start(self):
        """Start service.

        Here we spawn bjsonrpc serve thread, which will handle requests.
        """
        server = bjsonrpc.createserver(host=self.config.bind_host,
                                       port=self.config.bind_port,
                                       handler_factory=self)
        return gevent.spawn(server.serve)

    def loopback(self, data):
        """This is a method for shared services testing.

        It just returns what it gets as a parameter.
        """
        return data

    def serialize(self, data):
        """Make data ready for transmission."""
        return base64.encodestring(zlib.compress(cPickle.dumps(data)))
