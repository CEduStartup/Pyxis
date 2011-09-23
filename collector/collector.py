import gevent
import settings
import sys
import time

from gevent.backdoor import BackdoorServer
from Scheduler import Scheduler
from TrackerCollection import TrackerCollection
from storage import storage_types


storage_class = storage_types[settings.STORAGE_TYPE]
storage = storage_class(settings.STORAGE_HOST, settings.STORAGE_PORT,
                        settings.STORAGE_DB_NAME)
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

BackdoorServer((settings.BACKDOOR_HOST, settings.BACKDOOR_PORT)).serve_forever()

