import bjsonrpc
from bjsonrpc.handlers import BaseHandler
from random import random

class TrackersHandler(BaseHandler):
    def get_tracker_data(self, id, start=0, end=0, period=False, method=False):
        # Pseudocode
        return [int(str(random()*1000)[:2]) for i in xrange(12)]

s = bjsonrpc.createserver(handler_factory = TrackersHandler)
s.debug_socket(True)
s.serve()
