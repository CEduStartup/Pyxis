import gevent
import config.collector as collector_config
import config.storage as storage_config
import sys
import time

from gevent.backdoor import BackdoorServer
from Scheduler import Scheduler
from TrackerCollection import TrackerCollection
from shared.storage import storage_types


storage_class = storage_types[storage_config.storage_type]
storage = storage_class(storage_config.host, storage_config.port,
                        storage_config.db_name)
scheduler = Scheduler()
tracker_collection = TrackerCollection(scheduler, storage)

tracker_collection.start()
storage.start()
scheduler.start()

def handle_command_line_args():
    HELP = '--help'

    if HELP in sys.argv:
        print """\
Options:
--help - print this message without running app.
"""
        exit()

handle_command_line_args()

BackdoorServer((collector_config.backdoor_host, collector_config.backdoor_port)).serve_forever()

