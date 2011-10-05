import bjsonrpc
from bjsonrpc.handlers import BaseHandler
from django.conf import settings
from random import random

class TrackersHandler(BaseHandler):
    def get_tracker_data(self, id, start=0, end=0, period=False, method=False):
        # Pseudocode
        return [int(str(random()*1000000)[:2]) for i in xrange(12)]

s = bjsonrpc.createserver(host = settings.RPC_HOST,
                          port = settings.RPC_PORT,
                          handler_factory = TrackersHandler)
s.debug_socket(True)
s.serve()
